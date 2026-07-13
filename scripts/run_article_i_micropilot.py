"""Article-I micro-pilot (protocol section 7). Small diagnostic computation
allowed AFTER the literature gate and analytic benchmark.

For a few pre-chosen placements per symmetry class it saves the FULL signed
overlap matrix (not squared), reconstructs the 2x2 deformed doublet Hamiltonian
in the baseline doublet basis, estimates leakage, builds the finite-difference
response matrix A_delta = (H2_delta - H2_0)/delta, and reports its
basis-INVARIANT quantities (eigenvalues, trace, traceless Frobenius norm,
principal-axis angle) versus the continuum disk benchmark.

Forbidden: 64^2, wide grids, wide size series. This is O(100) tiny solves.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402

from src.article_g_signed_response import (  # noqa: E402
    placed_sites, semi_axes, solve_sites, symmetry_class,
)
from src.article_i_benchmark import DISK_CHIH_SPLIT, DISK_SLOPE_PAIR  # noqa: E402

OUT = PROJECT_ROOT / "reports" / "article_i_theory_gate"
SHAPES = (2.0, 4.0)
SIZES = (24.3, 33.7)
DELTAS = (0.01, 0.02, 0.04)  # small, fixed-delta, area-preserving
# a few placements per symmetry class (theta=0)
PLACEMENTS = {
    "C4v": [(0.0, 0.0), (0.5, 0.5)],
    "Cs_axis": [(0.5, 0.3), (0.0, 0.4)],
    "C1": [(0.31, 0.17), (0.23, 0.41), (0.6875, 0.75), (0.13, 0.62)],
}


def doublet_vectors(a_x, a_y, n, x0, y0):
    """Return (E0, E1, E2, v1, v2, site_index) for the placed domain."""
    sites = placed_sites(a_x, a_y, n, x0, y0, 0.0)
    spec = solve_sites(sites, k=4)
    idx = {s: i for i, s in enumerate(sites)}
    return spec.energies, spec.vectors, idx, sites


def embed(vecs, idx, cols, union_index, m):
    V = np.zeros((m, len(cols)))
    for tag, li in idx.items():
        for c, col in enumerate(cols):
            V[union_index[tag], c] = vecs[li, col]
    for c in range(len(cols)):
        nrm = np.linalg.norm(V[:, c])
        if nrm > 0:
            V[:, c] /= nrm
    return V


def response_for(n, a0, x0, y0, delta):
    # baseline (delta=0): a_x=a_y=a0
    e0, v0, idx0, s0 = doublet_vectors(a0, a0, n, x0, y0)
    ax, ay = semi_axes(a0, delta, "area_preserving")
    ed, vd, idxd, sd = doublet_vectors(ax, ay, n, x0, y0)

    union = sorted(set(s0) | set(sd))
    uindex = {s: i for i, s in enumerate(union)}
    m = len(union)
    V0 = embed(v0, idx0, (1, 2), uindex, m)   # baseline doublet
    Vd = embed(vd, idxd, (1, 2), uindex, m)   # deformed doublet

    # full signed overlap matrix (NOT squared)
    M = V0.T @ Vd                              # 2x2
    # deformed doublet Hamiltonian projected into the baseline doublet basis:
    # H2 = M diag(E_d1, E_d2) M^T  (valid when leakage is small)
    Ed = np.diag([ed[1] + 4.0, ed[2] + 4.0])   # kinetic scale E+4
    H2_delta = M @ Ed @ M.T
    H2_0 = np.diag([e0[1] + 4.0, e0[2] + 4.0])

    # leakage: how much deformed-doublet weight lies outside baseline doublet
    leak = 1.0 - float(np.mean(np.sum(M ** 2, axis=0)))
    sv = np.linalg.svd(M, compute_uv=False)

    A = (H2_delta - H2_0) / delta
    A = 0.5 * (A + A.T)                         # symmetrize (numerical)
    w = np.linalg.eigvalsh(A)                   # invariant eigenvalues
    k0 = e0[0] + 4.0                            # ground kinetic scale (baseline)
    w_dimless = w / k0
    trace = float(np.trace(A))
    traceless = A - 0.5 * trace * np.eye(2)
    tl_norm = float(np.linalg.norm(traceless))
    # principal-axis angle of the traceless part
    angle = 0.5 * math.degrees(math.atan2(2 * A[0, 1], A[0, 0] - A[1, 1]))
    return {
        "n": n, "a0": a0, "x0": x0, "y0": y0, "delta": delta,
        "symmetry_class_0": symmetry_class(x0, y0, 0.0),
        "n_sites_0": len(s0), "n_sites_delta": len(sd),
        "overlap_M11": M[0, 0], "overlap_M12": M[0, 1],
        "overlap_M21": M[1, 0], "overlap_M22": M[1, 1],
        "sv_min": float(sv.min()), "sv_max": float(sv.max()),
        "leakage": leak,
        "A_eig_lo": float(w[0]), "A_eig_hi": float(w[1]),
        "A_eig_lo_dimless": float(w_dimless[0]),
        "A_eig_hi_dimless": float(w_dimless[1]),
        "A_trace": trace, "A_traceless_norm": tl_norm,
        "A_traceless_norm_dimless": tl_norm / k0,
        "principal_axis_deg": angle,
        "invariant_split_dimless": float(w_dimless[1] - w_dimless[0]),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in SHAPES:
        for cls, plist in PLACEMENTS.items():
            for (x0, y0) in plist:
                for a0 in SIZES:
                    for delta in DELTAS:
                        try:
                            rows.append(response_for(n, a0, x0, y0, delta))
                        except Exception as exc:  # noqa: BLE001
                            rows.append({"n": n, "a0": a0, "x0": x0, "y0": y0,
                                         "delta": delta, "symmetry_class_0": cls,
                                         "leakage": float("nan"),
                                         "error": type(exc).__name__})
        print(f"micro-pilot n={n} done", flush=True)
    fields = sorted({k for r in rows for k in r})
    with open(OUT / "micropilot_response_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # summary: invariant split by symmetry class vs benchmark, smallest delta
    lines = ["# Article-I micro-pilot: 2x2 shape-derivative response invariants",
             "",
             f"Continuum disk benchmark: chih_split = {DISK_CHIH_SPLIT:.4f}, "
             f"invariant slope pair = ({DISK_SLOPE_PAIR[0]:.3f}, {DISK_SLOPE_PAIR[1]:.3f}).",
             "",
             "Invariant dimensionless split (A eigenvalue difference / ground scale),",
             "delta=0.01, mean over placements per class:",
             "",
             "| n | class | mean invariant split | mean traceless norm | max leakage | n |",
             "|---|---|---|---|---|---|"]
    for n in SHAPES:
        for cls in PLACEMENTS:
            sel = [r for r in rows if r.get("n") == n and r.get("symmetry_class_0") == cls
                   and abs(r.get("delta", 0) - 0.01) < 1e-9 and "A_eig_lo" in r]
            if not sel:
                continue
            isplit = np.mean([r["invariant_split_dimless"] for r in sel])
            tnorm = np.mean([r["A_traceless_norm_dimless"] for r in sel])
            maxleak = max(r["leakage"] for r in sel)
            lines.append(f"| {n} | {cls} | {isplit:.4f} | {tnorm:.4f} | {maxleak:.2e} | {len(sel)} |")
    (OUT / "micropilot_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("micro-pilot done:", len(rows), "rows")


if __name__ == "__main__":
    main()

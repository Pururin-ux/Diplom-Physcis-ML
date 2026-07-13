"""Article-Ib validation micro-pilot (frozen protocol).

Compares constructions of the projected deformed doublet Hamiltonian and the
resulting finite-difference response matrix A = (B - B0)/delta:
  - two-state truncation B2
  - multi-state Bk (k=4,8,16,32)
  - exact large-barrier compression Bexact = V0r^T (H_d+4) V0r
  - polar-transported BQ (Q = polar factor of the 2x2 overlap)
  - one-sided A_+ and symmetric A_sym
Reports basis-invariant quantities and their stability across constructions.
Small computation (allowed after the literature gate). No 64^2, no wide grids.
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
from scipy.sparse import lil_matrix, csc_matrix, identity  # noqa: E402
from scipy.sparse.linalg import eigsh  # noqa: E402

from src.article_g_signed_response import placed_sites, semi_axes, symmetry_class  # noqa: E402
from src.article_i_benchmark import DISK_CHIH_SPLIT  # noqa: E402

OUT = PROJECT_ROOT / "reports" / "article_ib_response_validation"
KMULTI = (2, 4, 8, 16, 32)
SHAPES = (2.0, 4.0)
SIZES = (24.3, 33.7)
BENCH_SIZES = (24.3, 33.7, 48.2)  # n=2 C4v only
DELTAS = (0.005, 0.01, 0.02)
PLACEMENTS = {
    "C4v": [(0.0, 0.0), (0.5, 0.5)],
    "Cs_axis": [(0.5, 0.3), (0.0, 0.4)],
    "C1": [(0.31, 0.17), (0.23, 0.41), (0.6875, 0.75), (0.13, 0.62)],
}


def build_H(sites):
    idx = {s: i for i, s in enumerate(sites)}
    n = len(sites)
    H = lil_matrix((n, n))
    for (x, y), i in idx.items():
        for dx, dy in ((1, 0), (0, 1)):
            j = idx.get((x + dx, y + dy))
            if j is not None:
                H[i, j] = -1.0
                H[j, i] = -1.0
    return csc_matrix(H), idx


def solve(sites, k):
    H, idx = build_H(sites)
    kk = min(k, H.shape[0] - 2)
    vals, vecs = eigsh(H, k=kk, sigma=-4.2, which="LM")
    o = np.argsort(vals)
    return vals[o], vecs[:, o], H, idx


def invariants(A, k0):
    w = np.linalg.eigvalsh(0.5 * (A + A.T))
    tr = float(np.trace(A))
    det = float(np.linalg.det(A))
    split = float(w[1] - w[0])
    tl = A - 0.5 * tr * np.eye(2)
    frob_tl = float(np.linalg.norm(tl))
    angle = 0.5 * math.degrees(math.atan2(2 * A[0, 1], A[0, 0] - A[1, 1]))
    return {
        "eig_lo": float(w[0]) / k0, "eig_hi": float(w[1]) / k0,
        "trace": tr / k0, "det": det / k0 ** 2, "split": split / k0,
        "frob_traceless": frob_tl / k0, "principal_axis_deg": angle,
    }


def overlaps(v0, idx0, vecs_d, idx_d, kcols):
    """M[i, j] = <baseline doublet i | deformed eigenstate j> on S0 ∩ Sd."""
    common = set(idx0) & set(idx_d)
    M = np.zeros((2, kcols))
    for s in common:
        a = v0[idx0[s], :]                      # (2,)
        b = vecs_d[idx_d[s], 1:1 + kcols]        # deformed excited states 1..kcols
        M += np.outer(a, b)
    return M


def bexact_largebarrier(v0, idx0, Hd, idx_d):
    """Bexact = V0r^T (Hd+4) V0r, V0r = baseline doublet restricted to Sd."""
    nd = Hd.shape[0]
    V0r = np.zeros((nd, 2))
    for s, j in idx_d.items():
        i0 = idx0.get(s)
        if i0 is not None:
            V0r[j, :] = v0[i0, :]
    Hp4 = Hd + 4.0 * identity(nd, format="csc")
    return V0r.T @ (Hp4 @ V0r)


def response_row(n, a0, x0, y0, delta):
    s0 = placed_sites(a0, a0, n, x0, y0, 0.0)
    e0, vec0, H0, idx0 = solve(s0, 34)
    v0 = vec0[:, [1, 2]]
    k0 = e0[0] + 4.0
    B0 = np.diag([e0[1] + 4.0, e0[2] + 4.0])

    ax, ay = semi_axes(a0, delta, "area_preserving")
    sd = placed_sites(ax, ay, n, x0, y0, 0.0)
    ed, vecd, Hd, idxd = solve(sd, 34)
    Ed_full = ed[1:1 + max(KMULTI)] + 4.0

    row = {
        "n": n, "a0": a0, "x0": x0, "y0": y0, "delta": delta,
        "symmetry_class_0": symmetry_class(x0, y0, 0.0),
        "n0": len(s0), "nd": len(sd),
        "added": len(set(sd) - set(s0)), "removed": len(set(s0) - set(sd)),
    }

    # multi-state constructions
    Mfull = overlaps(v0, idx0, vecd, idxd, max(KMULTI))
    row["leakage"] = 1.0 - float(np.sum(Mfull[:, :2] ** 2))  # weight outside deformed doublet
    for k in KMULTI:
        Mk = Mfull[:, :k]
        Bk = Mk @ np.diag(Ed_full[:k]) @ Mk.T
        Ak = (Bk - B0) / delta
        inv = invariants(Ak, k0)
        row[f"split_k{k}"] = inv["split"]
        row[f"frob_k{k}"] = inv["frob_traceless"]
        row[f"eiglo_k{k}"] = inv["eig_lo"]
        row[f"eighi_k{k}"] = inv["eig_hi"]

    # exact large-barrier compression
    Bex = bexact_largebarrier(v0, idx0, Hd, idxd)
    Aex = (Bex - B0) / delta
    inv = invariants(Aex, k0)
    row.update({f"exact_{key}": val for key, val in inv.items()})

    # polar transport of the 2-state construction
    M2 = Mfull[:, :2]
    U, S, Wt = np.linalg.svd(M2)
    Q = U @ Wt
    BQ = Q @ np.diag(Ed_full[:2]) @ Q.T
    AQ = (BQ - B0) / delta
    invQ = invariants(AQ, k0)
    row.update({f"polar_{key}": val for key, val in invQ.items()})
    row["sv_min_M2"] = float(S.min())
    row["sv_max_M2"] = float(S.max())
    return row, (Bex, B0, k0)


def sym_difference_row(n, a0, x0, y0, delta):
    """A_sym = (Bexact(+delta) - Bexact(-delta))/(2 delta) if S(-delta) valid."""
    _, (Bp, B0, k0) = response_row(n, a0, x0, y0, +delta)
    try:
        _, (Bm, _, _) = response_row(n, a0, x0, y0, -delta)
    except Exception:  # noqa: BLE001
        return None
    Asym = (Bp - Bm) / (2 * delta)
    Aplus = (Bp - B0) / delta
    return {
        "n": n, "a0": a0, "x0": x0, "y0": y0, "delta": delta,
        "symmetry_class_0": symmetry_class(x0, y0, 0.0),
        "split_plus": invariants(Aplus, k0)["split"],
        "split_sym": invariants(Asym, k0)["split"],
    }


def event_scan(n, a0, x0, y0, dmax=0.03, ndelta=61):
    """Dense delta scan: site count and Bexact-split vs delta for one placement."""
    s0 = placed_sites(a0, a0, n, x0, y0, 0.0)
    e0, vec0, H0, idx0 = solve(s0, 6)
    v0 = vec0[:, [1, 2]]
    k0 = e0[0] + 4.0
    B0 = np.diag([e0[1] + 4.0, e0[2] + 4.0])
    out = []
    prev_n = None
    for delta in np.linspace(0.0005, dmax, ndelta):
        ax, ay = semi_axes(a0, delta, "area_preserving")
        sd = placed_sites(ax, ay, n, x0, y0, 0.0)
        ed, vecd, Hd, idxd = solve(sd, 6)
        Bex = bexact_largebarrier(v0, idx0, Hd, idxd)
        A = (Bex - B0) / delta
        w = np.linalg.eigvalsh(0.5 * (A + A.T)) / k0
        event = 1 if (prev_n is not None and len(sd) != prev_n) else 0
        prev_n = len(sd)
        out.append({"n": n, "a0": a0, "x0": x0, "y0": y0, "delta": float(delta),
                    "nd": len(sd), "removed_vs0": len(set(s0) - set(sd)),
                    "event": event, "split": float(w[1] - w[0]),
                    "eig_lo": float(w[0]), "eig_hi": float(w[1])})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, symrows = [], []
    for n in SHAPES:
        for cls, plist in PLACEMENTS.items():
            for (x0, y0) in plist:
                for a0 in SIZES:
                    for delta in DELTAS:
                        r, _ = response_row(n, a0, x0, y0, delta)
                        rows.append(r)
                    sr = sym_difference_row(n, a0, x0, y0, 0.01)
                    if sr:
                        symrows.append(sr)
        print(f"validation n={n} done", flush=True)
    # benchmark trend: n=2 C4v at three sizes
    for a0 in BENCH_SIZES:
        for (x0, y0) in PLACEMENTS["C4v"]:
            for delta in DELTAS:
                r, _ = response_row(2.0, a0, x0, y0, delta)
                r["bench_set"] = 1
                rows.append(r)

    fields = sorted({k for r in rows for k in r})
    with open(OUT / "validation_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "validation_symdiff.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(symrows[0].keys()))
        w.writeheader()
        w.writerows(symrows)

    # event scans for 4 representative placements
    scan = []
    for (n, x0, y0) in [(2.0, 0.0, 0.0), (2.0, 0.31, 0.17),
                        (4.0, 0.0, 0.0), (4.0, 0.6875, 0.75)]:
        scan.extend(event_scan(n, 33.7, x0, y0))
    with open(OUT / "validation_event_scan.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(scan[0].keys()))
        w.writeheader()
        w.writerows(scan)
    print("validation done:", len(rows), "rows,", len(scan), "scan points")


if __name__ == "__main__":
    main()

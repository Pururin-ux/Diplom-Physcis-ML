"""Run article-F robustness checks R1-R4.

Frozen definitions: reports/article_f_boundary_realization/protocol_addendum_1.md
(committed before execution, commit 04e24a1).
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
from scipy.linalg import qr, svdvals  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402
from scipy.sparse.linalg import eigsh  # noqa: E402
from scipy.special import y0 as bessel_y0  # noqa: E402

from src.geometry import (  # noqa: E402
    build_superellipse_dot_placed,
    placed_superellipse_sites,
)
from src.kwant_solver import lowest_energies_of_system  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"
J01_SQ = 5.783185962946783

MFS_REFERENCE = {1.2: 6.040437, 2.0: 5.783186, 3.0: 5.866676, 4.0: 5.969020}
R2_TARGETS = {3.0: (5.21631971, 13.19017870), 4.0: (5.05703172, 12.73171703)}
R2_CHARGE_FACTORS = (1.15, 1.2, 1.3)
R2_BASIS_SIZES = (120, 200)
R3_N = (1.2, 4.0)
R3_SCALES = (24.0, 48.0)
R3_ANGLES = (0.0, 22.5, 45.0)
GRID_4 = tuple(i / 4 for i in range(4))
XI_GRID = [0.25 * k for k in range(0, 17)]
INTERIOR_POINTS = 60
RNG_SEED = 42


def area_factor(n: float) -> float:
    return 4.0 * math.gamma(1 + 1 / n) ** 2 / math.gamma(1 + 2 / n)


# ---------------------------------------------------------------- R1

def r1_extrapolation_robustness(lines: list[str]) -> None:
    rows = list(csv.DictReader(open(OUTPUT_DIR / "fixed_area_scaling_rows.csv")))
    lines.append("## R1. Extrapolation-form robustness")
    out_rows = []
    for n in (1.2, 2.0, 3.0, 4.0):
        sel = [r for r in rows if float(r["n"]) == n]
        scales = sorted({float(r["a_circ"]) for r in sel})
        means = np.array(
            [
                np.mean(
                    [float(r["lamA_an"]) for r in sel if float(r["a_circ"]) == s]
                )
                for s in scales
            ]
        )
        x = 1.0 / np.array(scales)
        lin = np.polyfit(x, means, 1)
        lin_resid = float(np.max(np.abs(np.polyval(lin, x) - means)))
        quad = np.polyfit(x, means, 2)
        intercepts = [lin[-1], quad[-1]]
        labels = ["linear", "quadratic"]
        for skip in range(len(scales)):
            xx = np.delete(x, skip)
            mm = np.delete(means, skip)
            loo = np.polyfit(xx, mm, 1)
            intercepts.append(loo[-1])
            labels.append(f"LOO drop a_circ={scales[skip]:.0f}")
        spread = max(intercepts) - min(intercepts)
        ref = MFS_REFERENCE[n]
        lines.append(
            f"- n={n}: linear={intercepts[0]:.4f} quad={intercepts[1]:.4f} "
            f"LOO range=[{min(intercepts[2:]):.4f}, {max(intercepts[2:]):.4f}] "
            f"full spread={spread:.4f} ({100 * spread / ref:.2f}% of MFS) "
            f"lin max resid={lin_resid:.4f}"
        )
        for lab, val in zip(labels, intercepts):
            out_rows.append(
                {
                    "n": n,
                    "variant": lab,
                    "intercept": val,
                    "vs_MFS_percent": 100 * (val / ref - 1),
                }
            )
    with open(OUTPUT_DIR / "r1_extrapolation_variants.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    lines.append("")


# ---------------------------------------------------------------- R2

def boundary_points(n: float, count: int, scale: float = 1.0) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    ct, st = np.cos(t), np.sin(t)
    x = np.sign(ct) * np.abs(ct) ** (2.0 / n)
    y = np.sign(st) * np.abs(st) ** (2.0 / n)
    return scale * np.column_stack([x, y])


def interior_points(n: float, count: int) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    pts: list[list[float]] = []
    while len(pts) < count:
        cand = rng.uniform(-1.0, 1.0, size=(count * 4, 2))
        mask = np.abs(cand[:, 0]) ** n + np.abs(cand[:, 1]) ** n <= 0.9
        pts.extend(cand[mask].tolist())
    return np.array(pts[:count])


def mfs_eigenvalue(
    n: float, k_center: float, n_charges: int, charge_factor: float
) -> float:
    bpts = boundary_points(n, 3 * n_charges)
    ipts = interior_points(n, INTERIOR_POINTS)
    charges = boundary_points(n, n_charges, scale=charge_factor)
    all_pts = np.vstack([bpts, ipts])
    dists = np.linalg.norm(all_pts[:, None, :] - charges[None, :, :], axis=2)
    n_b = len(bpts)

    def sigma(k: float) -> float:
        a_mat = bessel_y0(k * dists)
        q_mat, _ = qr(a_mat, mode="economic")
        return float(svdvals(q_mat[:n_b, :])[-1])

    res = minimize_scalar(
        sigma,
        bounds=(k_center - 0.02, k_center + 0.02),
        method="bounded",
        options={"xatol": 1e-11},
    )
    return float(res.x) ** 2


def r2_mfs_robustness(lines: list[str]) -> None:
    lines.append("## R2. MFS parameter robustness (n = 3.0, 4.0)")
    out_rows = []
    for n, (lam1_ref, lam2_ref) in R2_TARGETS.items():
        for which, lam_ref in (("lambda1", lam1_ref), ("lambda2", lam2_ref)):
            vals = []
            for cf in R2_CHARGE_FACTORS:
                for basis in R2_BASIS_SIZES:
                    lam = mfs_eigenvalue(n, math.sqrt(lam_ref), basis, cf)
                    vals.append(lam)
                    out_rows.append(
                        {
                            "n": n,
                            "eigenvalue": which,
                            "charge_factor": cf,
                            "basis": basis,
                            "value": lam,
                        }
                    )
            spread = max(vals) - min(vals)
            lines.append(
                f"- n={n} {which}: mean={np.mean(vals):.8f} "
                f"spread={spread:.2e} (rel {spread / np.mean(vals):.1e})"
            )
    with open(OUTPUT_DIR / "r2_mfs_robustness.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    lines.append("")


# ---------------------------------------------------------------- R3

def r3_orientation_decay(lines: list[str]) -> None:
    lines.append("## R3. Orientation-effect decay with size")
    out_rows = []
    stage1 = list(csv.DictReader(open(OUTPUT_DIR / "placement_stats_rows.csv")))
    for n in R3_N:
        deltas = {}
        for a_circ in R3_SCALES:
            a = math.sqrt(math.pi * a_circ * a_circ / area_factor(n))
            an_area = area_factor(n) * a * a
            theta_means = []
            for theta in R3_ANGLES:
                vals = []
                for dx in GRID_4:
                    for dy in GRID_4:
                        fsys = build_superellipse_dot_placed(
                            a, a, n, x0=dx, y0=dy, theta_deg=theta
                        )
                        ev = lowest_energies_of_system(fsys, k=4)
                        vals.append((ev[0] + 4.0) * an_area / math.pi)
                theta_means.append(np.mean(vals))
                out_rows.append(
                    {
                        "n": n,
                        "a_circ": a_circ,
                        "theta_deg": theta,
                        "lamA_an_mean": np.mean(vals),
                        "lamA_an_std": np.std(vals),
                    }
                )
            deltas[a_circ] = max(theta_means) - min(theta_means)
            print(f"R3 done n={n} a_circ={a_circ}")
        sel = [
            r
            for r in stage1
            if float(r["n"]) == n
            and float(r["theta_deg"]) in R3_ANGLES
            and float(r["x0"]) in GRID_4
            and float(r["y0"]) in GRID_4
        ]
        theta_means_30 = []
        for theta in R3_ANGLES:
            v = [
                float(r["lamA_an"])
                for r in sel
                if float(r["theta_deg"]) == theta
            ]
            theta_means_30.append(np.mean(v))
        deltas[30.0] = max(theta_means_30) - min(theta_means_30)
        scales = sorted(deltas)
        dv = np.array([deltas[s] for s in scales])
        p_fit = np.polyfit(np.log(np.array(scales)), np.log(dv), 1)
        lines.append(
            f"- n={n}: Delta_theta = "
            + ", ".join(f"{deltas[s]:.4f} (a_circ={s:.0f})" for s in scales)
            + f"; effective power p={-p_fit[0]:.2f} (3-point estimate)"
        )
    with open(OUTPUT_DIR / "r3_orientation_decay.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    lines.append("")


# ---------------------------------------------------------------- R4

def r4_sawtooth_weights(lines: list[str]) -> None:
    lines.append("## R4. Sawtooth mechanism: perturbative weight of removed sites")
    n, a = 4.0, 33.0
    prev = None
    steps = []
    for xi in XI_GRID:
        b = a * (1.0 - xi / a)
        sites = placed_superellipse_sites(a, b, n)
        fsys = build_superellipse_dot_placed(a, b, n)
        h = fsys.hamiltonian_submatrix(sparse=True).tocsc().real
        vals, vecs = eigsh(h, k=4, sigma=-4.2, which="LM")
        order = np.argsort(vals)
        vals, vecs = vals[order], vecs[:, order]
        tag_index = {tuple(s.tag): i for i, s in enumerate(fsys.sites)}
        state = {
            "xi": xi,
            "sites": set(sites),
            "vals": vals,
            "vecs": vecs,
            "tag_index": tag_index,
        }
        if prev is not None:
            removed = prev["sites"] - state["sites"]
            added = state["sites"] - prev["sites"]
            assert not added, "domain must shrink monotonically"
            idx = [prev["tag_index"][s] for s in removed]
            w1 = float(np.sum(prev["vecs"][idx, 1] ** 2))
            w2 = float(np.sum(prev["vecs"][idx, 2] ** 2))
            steps.append(
                {
                    "xi": xi,
                    "removed": len(removed),
                    "w1": w1,
                    "w2": w2,
                    "dE1": state["vals"][1] - prev["vals"][1],
                    "dE2": state["vals"][2] - prev["vals"][2],
                    "dSplit": (state["vals"][2] - state["vals"][1])
                    - (prev["vals"][2] - prev["vals"][1]),
                }
            )
        prev = state
    with open(OUTPUT_DIR / "r4_sawtooth_weights.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(steps[0].keys()))
        writer.writeheader()
        writer.writerows(steps)

    def pearson(x, y):
        x, y = np.array(x), np.array(y)
        return float(np.corrcoef(x, y)[0, 1])

    c_e1 = pearson([s["w1"] for s in steps], [s["dE1"] for s in steps])
    c_e2 = pearson([s["w2"] for s in steps], [s["dE2"] for s in steps])
    c_split = pearson(
        [s["w2"] - s["w1"] for s in steps], [s["dSplit"] for s in steps]
    )
    c_count = pearson(
        [s["removed"] for s in steps], [abs(s["dSplit"]) for s in steps]
    )
    lines.append(f"- corr(dE1, w1) = {c_e1:+.3f}")
    lines.append(f"- corr(dE2, w2) = {c_e2:+.3f}")
    lines.append(f"- corr(dSplit, w2 - w1) = {c_split:+.3f}")
    lines.append(f"- baseline corr(|dSplit|, removed count) = {c_count:+.3f}")
    supported = abs(c_split) > abs(c_count)
    lines.append(
        f"- frozen rule outcome: weighted mechanism "
        f"{'SUPPORTED' if supported else 'NOT SUPPORTED'} "
        "(weighted correlation vs raw-count baseline)"
    )
    lines.append("")


def main() -> None:
    lines = [
        "# Article-F robustness checks R1-R4",
        "",
        "Frozen definitions: protocol_addendum_1.md (commit 04e24a1).",
        "",
    ]
    r1_extrapolation_robustness(lines)
    print("R1 done")
    r2_mfs_robustness(lines)
    print("R2 done")
    r3_orientation_decay(lines)
    print("R3 done")
    r4_sawtooth_weights(lines)
    print("R4 done")
    (OUTPUT_DIR / "robustness_checks_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("robustness checks complete")


if __name__ == "__main__":
    main()

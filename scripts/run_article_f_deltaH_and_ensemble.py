"""Run article-F checks R5 (low-rank Delta-H doublet prediction) and R6
(placement-averaged xi response).

Frozen definitions: reports/article_f_boundary_realization/protocol_addendum_2.md
(committed before execution, commit f270595).
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402
from scipy.sparse.linalg import eigsh  # noqa: E402

from src.geometry import (  # noqa: E402
    build_superellipse_dot_placed,
    placed_superellipse_sites,
)
from src.kwant_solver import lowest_energies_of_system  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

N_VAL = 4.0
A_VAL = 33.0
XI_GRID = [0.25 * k for k in range(0, 17)]
GRID_4 = tuple(i / 4 for i in range(4))
NEIGHBOR_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def solve_with_vectors(a: float, b: float, n: float):
    fsys = build_superellipse_dot_placed(a, b, n)
    h = fsys.hamiltonian_submatrix(sparse=True).tocsc().real
    vals, vecs = eigsh(h, k=4, sigma=-4.2, which="LM")
    order = np.argsort(vals)
    tag_index = {tuple(s.tag): i for i, s in enumerate(fsys.sites)}
    return vals[order], vecs[:, order], tag_index


def r5_delta_h(lines: list[str]) -> None:
    lines.append("## R5. Low-rank Delta-H prediction in the doublet subspace")
    prev = None
    steps = []
    for xi in XI_GRID:
        b = A_VAL * (1.0 - xi / A_VAL)
        sites = set(placed_superellipse_sites(A_VAL, b, N_VAL))
        vals, vecs, tag_index = solve_with_vectors(A_VAL, b, N_VAL)
        if prev is not None:
            removed = prev["sites"] - sites
            assert sites <= prev["sites"], "domain must shrink"
            # cut bonds: removed site s with any neighbor m in the OLD domain
            bonds = []
            for s in removed:
                for dx, dy in NEIGHBOR_STEPS:
                    m = (s[0] + dx, s[1] + dy)
                    if m in prev["sites"] and (m, s) not in bonds:
                        bonds.append((s, m))
            def w_elem(i: int, j: int) -> float:
                acc = 0.0
                for s, m in bonds:
                    si, mi = prev["tag_index"][s], prev["tag_index"][m]
                    acc += (
                        prev["vecs"][si, i] * prev["vecs"][mi, j]
                        + prev["vecs"][mi, i] * prev["vecs"][si, j]
                    )
                return acc
            w00 = w_elem(0, 0)
            w11, w22, w12 = w_elem(1, 1), w_elem(2, 2), w_elem(1, 2)
            mat = np.array(
                [
                    [prev["vals"][1] + w11, w12],
                    [w12, prev["vals"][2] + w22],
                ]
            )
            pred12 = np.sort(np.linalg.eigvalsh(mat))
            act = vals
            d_split_act = (act[2] - act[1]) - (prev["vals"][2] - prev["vals"][1])
            d_split_pred = (pred12[1] - pred12[0]) - (
                prev["vals"][2] - prev["vals"][1]
            )
            steps.append(
                {
                    "xi": xi,
                    "removed": len(removed),
                    "cut_bonds": len(bonds),
                    "dE0_act": act[0] - prev["vals"][0],
                    "dE0_pred": w00,
                    "dE1_act": act[1] - prev["vals"][1],
                    "dE1_pred": pred12[0] - prev["vals"][1],
                    "dE2_act": act[2] - prev["vals"][2],
                    "dE2_pred": pred12[1] - prev["vals"][2],
                    "dSplit_act": d_split_act,
                    "dSplit_pred": d_split_pred,
                }
            )
        prev = {"sites": sites, "vals": vals, "vecs": vecs, "tag_index": tag_index}
    with open(OUTPUT_DIR / "r5_deltaH_steps.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(steps[0].keys()))
        writer.writeheader()
        writer.writerows(steps)

    def rel_errs(key: str) -> np.ndarray:
        return np.array(
            [
                abs(s[f"{key}_pred"] - s[f"{key}_act"]) / abs(s[f"{key}_act"])
                for s in steps
                if abs(s[f"{key}_act"]) > 1e-14
            ]
        )

    for key in ("dE0", "dE1", "dE2", "dSplit"):
        e = rel_errs(key)
        lines.append(
            f"- {key}: median rel err {np.median(e) * 100:.1f}%, "
            f"max {np.max(e) * 100:.1f}%"
        )
    corr = float(
        np.corrcoef(
            [s["dSplit_pred"] for s in steps], [s["dSplit_act"] for s in steps]
        )[0, 1]
    )
    med = float(np.median(rel_errs("dSplit")))
    lines.append(f"- Pearson corr(dSplit_pred, dSplit_act) = {corr:+.4f}")
    lines.append(
        "- frozen rule outcome: "
        + (
            "QUANTITATIVE (median dSplit rel err < 25%)"
            if med < 0.25
            else "qualitative agreement only (median dSplit rel err >= 25%)"
        )
    )
    lines.append("")


def r6_ensemble(lines: list[str]) -> None:
    lines.append("## R6. Placement-averaged xi response")
    rows = []
    for dx in GRID_4:
        for dy in GRID_4:
            for xi in XI_GRID[1:]:
                r = 1.0 - xi / A_VAL
                fsys = build_superellipse_dot_placed(
                    A_VAL, A_VAL * r, N_VAL, x0=dx, y0=dy
                )
                vals = lowest_energies_of_system(fsys, k=4)
                y = ((vals[2] - vals[1]) / (vals[0] + 4.0)) / (1.0 - r)
                rows.append({"dx": dx, "dy": dy, "xi": xi, "y": y})
        print(f"R6 done dx={dx}")
    with open(OUTPUT_DIR / "r6_ensemble_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dx", "dy", "xi", "y"])
        writer.writeheader()
        writer.writerows(rows)

    xis = XI_GRID[1:]
    single = [
        next(r["y"] for r in rows if r["dx"] == 0 and r["dy"] == 0 and r["xi"] == xi)
        for xi in xis
    ]
    mean_y = [
        float(np.mean([r["y"] for r in rows if r["xi"] == xi])) for xi in xis
    ]
    std_y = [float(np.std([r["y"] for r in rows if r["xi"] == xi])) for xi in xis]
    tv_single = float(np.sum(np.abs(np.diff(single))))
    tv_mean = float(np.sum(np.abs(np.diff(mean_y))))
    lines.append("| xi | y centered | ensemble mean | ensemble std |")
    lines.append("|---|---|---|---|")
    for xi, s, m, sd in zip(xis, single, mean_y, std_y):
        lines.append(f"| {xi:.2f} | {s:.3f} | {m:.3f} | {sd:.3f} |")
    lines.append("")
    lines.append(f"- TV(centered realization) = {tv_single:.2f}")
    lines.append(f"- TV(ensemble mean) = {tv_mean:.2f}")
    for xi in (0.25, 0.5, 0.75):
        frac = np.mean([r["y"] < 1.0 for r in rows if r["xi"] == xi])
        lines.append(f"- fraction of placements with y < 1 at xi={xi}: {frac:.2f}")
    lines.append("")


def main() -> None:
    lines = [
        "# Article-F checks R5-R6",
        "",
        "Frozen definitions: protocol_addendum_2.md (commit f270595).",
        "",
    ]
    r5_delta_h(lines)
    print("R5 done")
    r6_ensemble(lines)
    print("R6 done")
    (OUTPUT_DIR / "deltaH_and_ensemble_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("R5-R6 complete")


if __name__ == "__main__":
    main()

"""Run the article-F placement-statistics protocol (translations and rotations).

Frozen protocol: reports/article_f_boundary_realization/protocol.md, section 1.
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

from src.geometry import build_superellipse_dot_placed  # noqa: E402
from src.kwant_solver import (  # noqa: E402
    lowest_energies_of_system,
    shift_invert_consistency_error,
)

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

J01_SQ = 5.783185962946783
N_VALUES = (1.2, 4.0)
A_CIRC = 30.0
ANGLES_DEG = (0.0, 11.25, 22.5, 33.75, 45.0)
GRID_4 = tuple(i / 4 for i in range(4))
GRID_8 = tuple(i / 8 for i in range(8))

ROW_COLUMNS = [
    "n",
    "a",
    "theta_deg",
    "x0",
    "y0",
    "grid",
    "N_sites",
    "E0",
    "E1",
    "E2",
    "E3",
    "Ekin0",
    "lamA_sites",
    "lamA_an",
    "S_lat",
]


def area_factor(n: float) -> float:
    return 4.0 * math.gamma(1 + 1 / n) ** 2 / math.gamma(1 + 2 / n)


def fixed_area_semi_axis(n: float, a_circ: float) -> float:
    return math.sqrt(math.pi * a_circ * a_circ / area_factor(n))


def one_cell(n: float, a: float, theta: float, x0: float, y0: float, grid: str) -> dict:
    fsys = build_superellipse_dot_placed(a, a, n, x0=x0, y0=y0, theta_deg=theta)
    vals = lowest_energies_of_system(fsys, k=4)
    n_sites = len(fsys.sites)
    ekin0 = vals[0] + 4.0
    an_area = area_factor(n) * a * a
    return {
        "n": n,
        "a": a,
        "theta_deg": theta,
        "x0": x0,
        "y0": y0,
        "grid": grid,
        "N_sites": n_sites,
        "E0": vals[0],
        "E1": vals[1],
        "E2": vals[2],
        "E3": vals[3],
        "Ekin0": ekin0,
        "lamA_sites": ekin0 * n_sites / math.pi,
        "lamA_an": ekin0 * an_area / math.pi,
        "S_lat": (vals[2] - vals[1]) / ekin0,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    check_sys = build_superellipse_dot_placed(12.0, 12.0, 4.0, x0=0.5)
    solver_check = shift_invert_consistency_error(check_sys, k=4)

    rows: list[dict] = []
    for n in N_VALUES:
        a = fixed_area_semi_axis(n, A_CIRC)
        for dx in GRID_8:
            for dy in GRID_8:
                grid = "8x8" if (dx not in GRID_4 or dy not in GRID_4) else "4x4+8x8"
                rows.append(one_cell(n, a, 0.0, dx, dy, grid))
        for theta in ANGLES_DEG[1:]:
            for dx in GRID_4:
                for dy in GRID_4:
                    rows.append(one_cell(n, a, theta, dx, dy, "4x4"))

    with open(OUTPUT_DIR / "placement_stats_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ROW_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    summary_lines = [
        "# Placement statistics summary (article F, protocol section 1)",
        "",
        f"- solver shift-invert vs SA max abs diff (startup check): {solver_check:.3e}",
        f"- fixed-area scale a_circ = {A_CIRC}",
        "",
    ]
    agg_rows = []
    for n in N_VALUES:
        for theta in ANGLES_DEG:
            if theta == 0.0:
                sel4 = [
                    r
                    for r in rows
                    if r["n"] == n
                    and r["theta_deg"] == 0.0
                    and r["x0"] in GRID_4
                    and r["y0"] in GRID_4
                ]
                sel8 = [r for r in rows if r["n"] == n and r["theta_deg"] == 0.0]
                for tag, sel in (("4x4", sel4), ("8x8", sel8)):
                    for key in ("lamA_sites", "lamA_an", "S_lat"):
                        v = np.array([r[key] for r in sel])
                        agg_rows.append(
                            {
                                "n": n,
                                "theta_deg": theta,
                                "grid": tag,
                                "quantity": key,
                                "mean": v.mean(),
                                "std": v.std(),
                                "min": v.min(),
                                "max": v.max(),
                                "count": len(v),
                            }
                        )
            else:
                sel = [r for r in rows if r["n"] == n and r["theta_deg"] == theta]
                for key in ("lamA_sites", "lamA_an", "S_lat"):
                    v = np.array([r[key] for r in sel])
                    agg_rows.append(
                        {
                            "n": n,
                            "theta_deg": theta,
                            "grid": "4x4",
                            "quantity": key,
                            "mean": v.mean(),
                            "std": v.std(),
                            "min": v.min(),
                            "max": v.max(),
                            "count": len(v),
                        }
                    )

    with open(OUTPUT_DIR / "placement_stats_aggregates.csv", "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "n",
                "theta_deg",
                "grid",
                "quantity",
                "mean",
                "std",
                "min",
                "max",
                "count",
            ],
        )
        writer.writeheader()
        writer.writerows(agg_rows)

    for n in N_VALUES:
        summary_lines.append(f"## n = {n}")
        for row in agg_rows:
            if row["n"] == n and row["quantity"] == "lamA_an":
                summary_lines.append(
                    f"- theta={row['theta_deg']:6.2f} grid={row['grid']}: "
                    f"lamA_an mean={row['mean']:.4f} std={row['std']:.4f} "
                    f"range=[{row['min']:.4f}, {row['max']:.4f}] (count {row['count']})"
                )
        for row in agg_rows:
            if row["n"] == n and row["quantity"] == "S_lat":
                summary_lines.append(
                    f"- theta={row['theta_deg']:6.2f} grid={row['grid']}: "
                    f"S_lat mean={row['mean']:.5f} max={row['max']:.5f}"
                )
        summary_lines.append("")

    (OUTPUT_DIR / "placement_stats_summary.md").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )
    print("placement stats done:", len(rows), "cells; solver check", solver_check)


if __name__ == "__main__":
    main()

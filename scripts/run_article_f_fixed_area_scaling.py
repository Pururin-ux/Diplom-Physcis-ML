"""Run the article-F fixed-area multi-scale series with translation averaging.

Frozen protocol: reports/article_f_boundary_realization/protocol.md, section 2.
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
from src.kwant_solver import lowest_energies_of_system  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

J01_SQ = 5.783185962946783
N_VALUES = (1.2, 2.0, 3.0, 4.0)
SCALES = (24.0, 30.0, 36.0, 48.0)
EXTRA_SCALE = 72.0
EXTRA_SCALE_N = (1.2, 4.0)
GRID_4 = tuple(i / 4 for i in range(4))


def area_factor(n: float) -> float:
    return 4.0 * math.gamma(1 + 1 / n) ** 2 / math.gamma(1 + 2 / n)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    cases = [(n, s) for n in N_VALUES for s in SCALES]
    cases += [(n, EXTRA_SCALE) for n in EXTRA_SCALE_N]
    for n, a_circ in cases:
        a = math.sqrt(math.pi * a_circ * a_circ / area_factor(n))
        an_area = area_factor(n) * a * a
        for dx in GRID_4:
            for dy in GRID_4:
                fsys = build_superellipse_dot_placed(a, a, n, x0=dx, y0=dy)
                vals = lowest_energies_of_system(fsys, k=4)
                ekin0 = vals[0] + 4.0
                n_sites = len(fsys.sites)
                rows.append(
                    {
                        "n": n,
                        "a_circ": a_circ,
                        "a": a,
                        "x0": dx,
                        "y0": dy,
                        "N_sites": n_sites,
                        "E0": vals[0],
                        "Ekin0": ekin0,
                        "lamA_sites": ekin0 * n_sites / math.pi,
                        "lamA_an": ekin0 * an_area / math.pi,
                    }
                )
        print(f"done n={n} a_circ={a_circ}")

    with open(OUTPUT_DIR / "fixed_area_scaling_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    agg = []
    for n, a_circ in cases:
        sel = [r for r in rows if r["n"] == n and r["a_circ"] == a_circ]
        for key in ("lamA_sites", "lamA_an"):
            v = np.array([r[key] for r in sel])
            agg.append(
                {
                    "n": n,
                    "a_circ": a_circ,
                    "quantity": key,
                    "mean": v.mean(),
                    "std": v.std(),
                    "min": v.min(),
                    "max": v.max(),
                }
            )
    with open(OUTPUT_DIR / "fixed_area_scaling_aggregates.csv", "w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["n", "a_circ", "quantity", "mean", "std", "min", "max"]
        )
        writer.writeheader()
        writer.writerows(agg)

    lines = ["# Fixed-area multi-scale series (article F, protocol section 2)", ""]
    fits = []
    for n in N_VALUES:
        scales = list(SCALES) + ([EXTRA_SCALE] if n in EXTRA_SCALE_N else [])
        means = []
        stds = []
        for a_circ in scales:
            m = next(
                r
                for r in agg
                if r["n"] == n and r["a_circ"] == a_circ and r["quantity"] == "lamA_an"
            )
            means.append(m["mean"])
            stds.append(m["std"])
        inv_a = np.array([1.0 / s for s in scales])
        coeffs = np.polyfit(inv_a, np.array(means), 1)
        intercept = coeffs[1]
        slope = coeffs[0]
        std_fit = np.polyfit(
            np.log(np.array(scales)), np.log(np.array(stds)), 1
        )
        fits.append(
            {
                "n": n,
                "lamA_an_intercept": intercept,
                "lamA_an_slope_vs_inv_a": slope,
                "std_power_exponent": std_fit[0],
            }
        )
        lines.append(f"## n = {n}")
        for a_circ, m, s in zip(scales, means, stds):
            lines.append(
                f"- a_circ={a_circ:5.0f}: lamA_an mean={m:.4f} std={s:.4f}"
            )
        lines.append(
            f"- linear extrapolation vs 1/a_circ: intercept={intercept:.4f} "
            f"(slope {slope:.3f}); std ~ a^{std_fit[0]:.2f}"
        )
        lines.append(
            f"- intercept excess over disk j01^2: "
            f"{100 * (intercept / J01_SQ - 1):+.2f}%"
        )
        lines.append("")

    with open(OUTPUT_DIR / "fixed_area_scaling_fits.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fits[0].keys()))
        writer.writeheader()
        writer.writerows(fits)

    (OUTPUT_DIR / "fixed_area_scaling_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("fixed-area scaling done:", len(rows), "cells")


if __name__ == "__main__":
    main()

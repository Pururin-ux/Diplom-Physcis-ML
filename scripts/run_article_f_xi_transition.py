"""Run the article-F xi-transition scan with site-set symmetric differences.

Frozen protocol: reports/article_f_boundary_realization/protocol.md, section 3.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.geometry import (  # noqa: E402
    build_superellipse_dot_placed,
    placed_superellipse_sites,
)
from src.kwant_solver import lowest_energies_of_system  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

CASES = [
    (4.0, 24.0),
    (4.0, 33.0),
    (4.0, 48.0),
    (1.2, 33.0),
    (2.0, 33.0),
    (3.0, 33.0),
]
XI_GRID = [0.25 * k for k in range(0, 17)]  # xi = 0 included as reference


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for n, a in CASES:
        prev_sites: set | None = None
        ref_sites: set | None = None
        ref_doublet_mean = None
        for xi in XI_GRID:
            r = 1.0 - xi / a
            b = a * r
            sites = set(placed_superellipse_sites(a, b, n))
            fsys = build_superellipse_dot_placed(a, b, n)
            vals = lowest_energies_of_system(fsys, k=4)
            ekin0 = vals[0] + 4.0
            s_val = (vals[2] - vals[1]) / ekin0
            doublet_mean = 0.5 * (vals[1] + vals[2])
            if ref_sites is None:
                ref_sites = sites
                ref_doublet_mean = doublet_mean
            added = len(sites - prev_sites) if prev_sites is not None else 0
            removed = len(prev_sites - sites) if prev_sites is not None else 0
            rows.append(
                {
                    "n": n,
                    "a": a,
                    "xi": xi,
                    "r_AR": r,
                    "N_sites": len(sites),
                    "added_vs_prev": added,
                    "removed_vs_prev": removed,
                    "dN_sym_vs_prev": added + removed,
                    "dN_sym_vs_ref": len(sites ^ ref_sites),
                    "E0": vals[0],
                    "E1": vals[1],
                    "E2": vals[2],
                    "S": s_val,
                    "S_over_1mr": s_val / (1.0 - r) if xi > 0 else 0.0,
                    "doublet_mean_shift": doublet_mean - ref_doublet_mean,
                }
            )
            prev_sites = sites
        print(f"done n={n} a={a}")

    with open(OUTPUT_DIR / "xi_transition_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# xi-transition scan with site-set symmetric differences",
        "",
        "Columns: y = S/(1-r); dN_sym counts sites entering/leaving between",
        "adjacent xi grid points (step 0.25).",
        "",
    ]
    for n, a in CASES:
        lines.append(f"## n = {n}, a = {a:.0f}")
        lines.append("| xi | y = S/(1-r) | dN_sym vs prev | N_sites |")
        lines.append("|---|---|---|---|")
        for row in rows:
            if row["n"] == n and row["a"] == a and row["xi"] > 0:
                lines.append(
                    f"| {row['xi']:.2f} | {row['S_over_1mr']:.3f} "
                    f"| {row['dN_sym_vs_prev']} | {row['N_sites']} |"
                )
        lines.append("")

    (OUTPUT_DIR / "xi_transition_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("xi transition done:", len(rows), "rows")


if __name__ == "__main__":
    main()

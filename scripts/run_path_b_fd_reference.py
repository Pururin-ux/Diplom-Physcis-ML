"""Run the finite-difference continuum reference step for Article Path B."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.path_b_fd_reference import GRID_VALUES, N_VALUES, run_fd_reference  # noqa: E402


OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_path_b_tb_continuum_scaling"

GRID_COLUMNS = [
    "n",
    "rAR",
    "N_grid",
    "h",
    "num_interior_points",
    "level_index",
    "lambda_fd_unit",
    "lambda_bessel_unit_if_available",
    "abs_error_vs_bessel_if_available",
    "rel_error_vs_bessel_if_available",
    "degeneracy_group_if_available",
]

VALUES_COLUMNS = [
    "n",
    "rAR",
    "N_grid_selected",
    "h",
    "level_index",
    "lambda_fd_unit",
    "degeneracy_group_if_available",
    "validation_status",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write CSV rows with stable columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _bessel_validation_lines(rows: list[dict[str, object]]) -> list[str]:
    """Return Markdown table rows for n=2 Bessel validation."""
    lines = [
        "| N_grid | level | lambda_fd_unit | lambda_bessel | rel_error | group |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        if float(row["n"]) != 2.0:
            continue
        lines.append(
            "| "
            f"{int(row['N_grid'])} | {int(row['level_index'])} | "
            f"{float(row['lambda_fd_unit']):.10g} | "
            f"{float(row['lambda_bessel_unit_if_available']):.10g} | "
            f"{float(row['rel_error_vs_bessel_if_available']):.6g} | "
            f"{row['degeneracy_group_if_available']} |"
        )
    return lines


def _selected_reference_lines(rows: list[dict[str, object]]) -> list[str]:
    """Return Markdown table rows for selected references."""
    lines = [
        "| n | level | N_grid | h | lambda_fd_unit | group |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{float(row['n']):.1f} | {int(row['level_index'])} | "
            f"{int(row['N_grid_selected'])} | {float(row['h']):.6g} | "
            f"{float(row['lambda_fd_unit']):.10g} | "
            f"{row['degeneracy_group_if_available']} |"
        )
    return lines


def write_summary(path: Path, result: dict[str, object]) -> None:
    """Write the FD reference summary."""
    circle = result["circle_error_summary"]
    lines = [
        "# FD Continuum Reference Summary",
        "",
        "## Scope",
        "",
        "This is the Article Path B FD-reference-only step. It implements and",
        "validates a finite-difference Dirichlet Laplacian continuum reference.",
        "It does not validate Path B, does not run tight-binding spectra, does not",
        "run shape contrast, does not fit an effective radius, does not use ML,",
        "and does not use Q or S objectives.",
        "",
        "## FD Method",
        "",
        "- Unit-scaled superellipse domain: `|X|^n + |Y/rAR|^n < 1`.",
        "- `rAR = 1.0` for this step.",
        "- Uniform Cartesian grid on `[-1, 1] x [-1, 1]`.",
        "- Strict interior points are unknowns; outside and boundary points impose",
        "  Dirichlet zero values.",
        "- Positive 5-point finite-difference Laplacian `-Delta`.",
        "- Lowest six eigenvalues computed with sparse `eigsh`.",
        "",
        "## Grid Resolutions",
        "",
        f"- N_grid values: `{GRID_VALUES}`",
        f"- n values: `{N_VALUES}`",
        "",
        "## Bessel Validation for n=2 Circle",
        "",
        *_bessel_validation_lines(result["grid_convergence_rows"]),
        "",
        "At the selected highest grid:",
        "",
        f"- selected N_grid: `{int(circle['N_grid'])}`",
        f"- ground-state relative error: `{circle['ground_rel_error']}`",
        f"- max low-level relative error: `{circle['max_low_level_rel_error']}`",
        f"- max low-level absolute error: `{circle['max_low_level_abs_error']}`",
        "",
        "## Degeneracy Handling",
        "",
        "Individual FD levels are reported. Degenerate Bessel groups are labeled for",
        "the circle, and splitting is reported rather than hidden.",
        "",
        f"- selected-grid Bessel-group splitting: `{result['bessel_group_splitting']}`",
        "",
        "## Final Chosen Reference Values",
        "",
        *_selected_reference_lines(result["selected_reference_rows"]),
        "",
        "## Stability Across Two Finest Grids",
        "",
        f"- max relative level change by n: `{result['two_finest_stability']}`",
        "",
        "## Limitations",
        "",
        "- This is a finite-difference reference on embedded Cartesian masks, not an",
        "  analytic continuum solution for `n != 2`.",
        "- The reference is not yet compared against tight-binding residuals.",
        "- This step does not establish n-dependent finite-lattice structure.",
        "- Degenerate continuum levels can be split by grid anisotropy; both levels",
        "  must remain visible in downstream analysis.",
        "",
        "## Effective-Radius Baseline Warning",
        "",
        "The next executable shape-contrast step must test:",
        "",
        "```text",
        "E_kin,0(a,n) = lambda_ref_0(n) / (a + delta_n)^2",
        "```",
        "",
        "and compute:",
        "",
        "```text",
        "R_eff(a,n) = E_kin,0(a,n) - lambda_ref_0(n)/(a + delta_n)^2",
        "```",
        "",
        "Path B must be killed as `KILLED_EFFECTIVE_RADIUS_BASELINE` if:",
        "",
        "- the effective-radius fit explains the TB spectra for all tested n;",
        "- `delta_n` is stable across a;",
        "- `delta_n` is predicted by perimeter, `N_boundary`, area pixelation, or",
        "  boundary pixelation proxy;",
        "- `R_eff` has no remaining systematic n-dependent structure.",
        "",
        "## Final Verdict",
        "",
        f"`{result['verdict']}`",
        "",
        "Reasons:",
        "",
        *[f"- {reason}" for reason in result["verdict_reasons"]],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the FD-reference-only step."""
    result = run_fd_reference()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "fd_reference_grid_convergence.csv", result["grid_convergence_rows"], GRID_COLUMNS)
    write_csv(OUTPUT_DIR / "fd_reference_values.csv", result["selected_reference_rows"], VALUES_COLUMNS)
    write_summary(OUTPUT_DIR / "fd_reference_summary.md", result)
    print(f"verdict: {result['verdict']}")
    print(f"selected_N_grid: {int(result['circle_error_summary']['N_grid'])}")
    print(f"circle_ground_rel_error: {result['circle_error_summary']['ground_rel_error']}")
    for reason in result["verdict_reasons"]:
        print(f"reason: {reason}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

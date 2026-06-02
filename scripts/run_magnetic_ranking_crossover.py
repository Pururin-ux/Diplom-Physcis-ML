"""Run the exploratory direct-Kwant magnetic ranking-crossover sprint."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.magnetic_ranking_crossover import (  # noqa: E402
    ALL_ALPHAS,
    BASELINE_COLUMNS,
    CROSSOVER_COLUMNS,
    DIAGNOSTIC_ALPHAS,
    GAUGE_CHECK_COLUMNS,
    RANKING_COLUMNS,
    RESPONSE_COLUMNS,
    ROBUSTNESS_COLUMNS,
    SPECTRA_COLUMNS,
    SHAPES,
    SYMMETRY_COLUMNS,
    WEAK_ALPHAS,
    run_magnetic_sprint,
)


OUTPUT_DIR = PROJECT_ROOT / "reports" / "magnetic_ranking_crossover"


def _format_value(value: object) -> object:
    """Format infinities consistently for CSV output."""
    if value == float("inf"):
        return "inf"
    return value


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write rows with a stable column order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_value(row.get(column, "")) for column in columns})


def write_sanity_checks(path: Path, result: dict[str, object]) -> None:
    """Write numerical sanity checks as a compact Markdown file."""
    sanity = result["sanity"]
    lines = [
        "# Magnetic Sprint Sanity Checks",
        "",
        "This file records numerical checks only. It is not a scientific result by itself.",
        "",
        "## Required Checks",
        "",
        f"- alpha0_reproduction_passed: `{sanity['alpha0_passed']}`",
        f"- max_alpha0_reproduction_error: `{sanity['max_alpha0_reproduction_error']}`",
        f"- alpha0_tolerance: `{sanity['alpha0_tolerance']}`",
        f"- hermiticity_passed: `{sanity['hermiticity_passed']}`",
        f"- max_hermiticity_error: `{sanity['max_hermiticity_error']}`",
        f"- hermiticity_tolerance: `{sanity['hermiticity_tolerance']}`",
        f"- eigen_imag_passed: `{sanity['eigen_imag_passed']}`",
        f"- max_eigen_imag: `{sanity['max_eigen_imag']}`",
        f"- eigen_imag_tolerance: `{sanity['eigen_imag_tolerance']}`",
        f"- gauge_invariance_passed: `{sanity['gauge_passed']}`",
        f"- max_gauge_invariance_error: `{sanity['max_gauge_invariance_error']}`",
        f"- gauge_tolerance: `{sanity['gauge_tolerance']}`",
        f"- finite_sorted_passed: `{sanity['finite_sorted_passed']}`",
        f"- numerical_passed: `{sanity['numerical_passed']}`",
        "",
        "## Field Diagnostics",
        "",
        f"- l_B_filter_status: {result['l_b_filter_status']}",
        f"- phi_total_min: `{result['phi_total_min']}`",
        f"- phi_total_max: `{result['phi_total_max']}`",
        "",
        "If any required numerical check fails, the sprint verdict must be `KILLED_NUMERICAL`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _count_true(rows: list[dict[str, object]], key: str) -> int:
    return sum(1 for row in rows if bool(row.get(key, False)))


def write_summary(path: Path, result: dict[str, object]) -> None:
    """Write the final sprint summary with one verdict."""
    shapes = ", ".join(f"{shape.shape_id} (n={shape.n}, rAR={shape.aspect_ratio})" for shape in SHAPES)
    crossovers = result["ranking_crossovers"]
    divergences = result["robustness_divergence"]
    thresholded_crossovers = _count_true(crossovers, "thresholded")
    qualified_crossovers = _count_true(crossovers, "qualifies_before_size_stability")
    robustness_candidates = _count_true(divergences, "weak_field_separation")
    qualified_divergences = _count_true(divergences, "qualifies_before_size_stability")
    lines = [
        "# Magnetic Ranking-Crossover Sprint Summary",
        "",
        f"Final verdict: `{result['verdict']}`",
        "",
        f"Verdict reason: {result['verdict_reason']}",
        "",
        "## Scope",
        "",
        "This was an exploratory direct-Kwant falsification sprint. It was not an ML",
        "task, not inverse screening, and not a rescue run for the closed Q/S line.",
        "",
        f"- Geometries: {shapes}",
        "- Sizes: `a = {30, 36}`",
        f"- Weak-field alpha grid: `{WEAK_ALPHAS}`",
        f"- Diagnostic alpha grid: `{DIAGNOSTIC_ALPHAS}`",
        f"- All alpha values computed: `{ALL_ALPHAS}`",
        "",
        "## Numerical Status",
        "",
        f"- alpha=0 reproduced zero-field spectra: `{result['sanity']['alpha0_passed']}`",
        f"- gauge invariance passed: `{result['sanity']['gauge_passed']}`",
        f"- maximum gauge difference: `{result['sanity']['max_gauge_invariance_error']}`",
        f"- Hamiltonian Hermiticity passed: `{result['sanity']['hermiticity_passed']}`",
        f"- eigenvalue imaginary-part check passed: `{result['sanity']['eigen_imag_passed']}`",
        f"- finite sorted spectra passed: `{result['sanity']['finite_sorted_passed']}`",
        "",
        "## Field Diagnostics",
        "",
        f"- l_B filter status: {result['l_b_filter_status']}",
        f"- phi_total range: `{result['phi_total_min']}` to `{result['phi_total_max']}`",
        "",
        "## Signal Diagnostics",
        "",
        f"- thresholded pairwise ranking crossovers: `{thresholded_crossovers}`",
        f"- crossovers surviving pre-size filters: `{qualified_crossovers}`",
        f"- robustness-divergence candidates: `{robustness_candidates}`",
        f"- robustness divergences surviving pre-size filters: `{qualified_divergences}`",
        "",
        "The strongest baseline remains the fixed zero-field geometry/aspect-ratio",
        "ranking unless a thresholded weak-field signal survives the explicit killer",
        "baseline filters and both sizes.",
        "",
        "No Q/S final outputs, preregistration files, or thesis files are modified by",
        "this sprint.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the sprint and write all requested outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = run_magnetic_sprint()

    write_csv(OUTPUT_DIR / "magnetic_spectra.csv", result["magnetic_spectra"], SPECTRA_COLUMNS)
    write_csv(OUTPUT_DIR / "gauge_invariance_check.csv", result["gauge_invariance_check"], GAUGE_CHECK_COLUMNS)
    write_csv(OUTPUT_DIR / "gap_rankings_by_alpha.csv", result["gap_rankings_by_alpha"], RANKING_COLUMNS)
    write_csv(OUTPUT_DIR / "ranking_crossovers.csv", result["ranking_crossovers"], CROSSOVER_COLUMNS)
    write_csv(OUTPUT_DIR / "robustness_divergence.csv", result["robustness_divergence"], ROBUSTNESS_COLUMNS)
    write_csv(OUTPUT_DIR / "magnetic_response_summary.csv", result["magnetic_response_summary"], RESPONSE_COLUMNS)
    write_csv(
        OUTPUT_DIR / "symmetry_artifact_diagnostics.csv",
        result["symmetry_artifact_diagnostics"],
        SYMMETRY_COLUMNS,
    )
    write_csv(OUTPUT_DIR / "baseline_comparison.csv", result["baseline_comparison"], BASELINE_COLUMNS)
    write_sanity_checks(OUTPUT_DIR / "sanity_checks.md", result)
    write_summary(OUTPUT_DIR / "summary.md", result)

    print(f"final_verdict: {result['verdict']}")
    print(f"verdict_reason: {result['verdict_reason']}")
    print(f"alpha0_passed: {result['sanity']['alpha0_passed']}")
    print(f"gauge_passed: {result['sanity']['gauge_passed']}")
    print(f"max_gauge_invariance_error: {result['sanity']['max_gauge_invariance_error']}")
    print(f"phi_total_range: {result['phi_total_min']}..{result['phi_total_max']}")
    print(f"l_B_filter_status: {result['l_b_filter_status']}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

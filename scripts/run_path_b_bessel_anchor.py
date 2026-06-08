"""Run only the Article Path B Bessel-anchor sprint."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.path_b_bessel_anchor import ANCHOR_ASPECT_RATIO, ANCHOR_N, ANCHOR_SIZES, run_bessel_anchor  # noqa: E402


OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_path_b_tb_continuum_scaling"

SPECTRA_COLUMNS = [
    "a",
    "level_index",
    "E_TB",
    "E_kin_TB",
    "lambda_bessel",
    "lambda_bessel_over_a2",
    "residual",
    "scaled_Ekin",
    "scaled_residual",
    "degeneracy_group",
]

FIT_COLUMNS = [
    "level_or_group",
    "fit_model",
    "exponent_p",
    "coefficient_c",
    "intercept_if_used",
    "R2",
    "RMSE",
    "leave_one_size_out_p_min",
    "leave_one_size_out_p_max",
    "leave_one_size_out_stable_true_false",
    "verdict_for_level",
]


def _format(value: object) -> object:
    """Format NaN values consistently for CSV output."""
    try:
        if value != value:
            return "nan"
    except TypeError:
        return value
    return value


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write rows with stable column order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format(row.get(column, "")) for column in columns})


def _residual_decrease_lines(spectra_rows: list[dict[str, object]]) -> list[str]:
    """Return Markdown lines summarizing residual magnitude decrease by level."""
    lines: list[str] = []
    for level_index in sorted({int(row["level_index"]) for row in spectra_rows}):
        rows = sorted(
            [row for row in spectra_rows if int(row["level_index"]) == level_index],
            key=lambda row: float(row["a"]),
        )
        first_abs = abs(float(rows[0]["residual"]))
        last_abs = abs(float(rows[-1]["residual"]))
        ratio = last_abs / first_abs if first_abs > 0.0 else float("nan")
        lines.append(
            f"- level_{level_index}: |R(a=96)| / |R(a=24)| = `{ratio:.6g}`"
        )
    return lines


def _fit_summary_lines(fit_rows: list[dict[str, object]]) -> list[str]:
    """Return compact fit diagnostics for abs-power fits."""
    lines: list[str] = []
    for row in fit_rows:
        if row["fit_model"] != "abs_power_law":
            continue
        lines.append(
            "- "
            f"{row['level_or_group']}: p=`{float(row['exponent_p']):.6g}`, "
            f"LOO p range=`{float(row['leave_one_size_out_p_min']):.6g}`.."
            f"`{float(row['leave_one_size_out_p_max']):.6g}`, "
            f"verdict=`{row['verdict_for_level']}`"
        )
    return lines


def write_summary(path: Path, result: dict[str, object]) -> None:
    """Write the Bessel-anchor sprint summary."""
    checks = result["numerical_checks"]
    degeneracy = result["degeneracy_summary"]
    lines = [
        "# Bessel Anchor Summary",
        "",
        "## Protocol Status",
        "",
        "This is the Article Path B `BESSEL_ANCHOR_ONLY` sprint. It does not run",
        "the full Path B pilot, does not compare superellipse exponents, does not",
        "use ML, and does not use Q or S objectives.",
        "",
        "## Tested Geometry",
        "",
        f"- n: `{ANCHOR_N}`",
        f"- rAR: `{ANCHOR_ASPECT_RATIO}`",
        "- shape: circular superellipse anchor",
        f"- sizes: `{ANCHOR_SIZES}`",
        "",
        "## Bessel Reference Definition",
        "",
        "Continuum Dirichlet disk eigenvalues are",
        "",
        "```text",
        "lambda_{m,s} = j_{m,s}^2 / a^2",
        "```",
        "",
        "with non-degenerate `m=0` levels and twofold-degenerate `m>0` levels.",
        "The first six continuum disk levels, including degeneracies, were used.",
        "",
        "## Degeneracy Handling",
        "",
        f"- degeneracy reported: `{degeneracy['degeneracy_reported']}`",
        f"- groups: `{degeneracy['group_sizes']}`",
        f"- max TB splitting by degenerate group: `{degeneracy['max_tb_splitting_by_degenerate_group']}`",
        "",
        "Individual residuals and group-averaged residual fits are both reported.",
        "",
        "## Numerical Sanity Checks",
        "",
        f"- spectra finite and sorted: `{checks['spectra_finite_sorted']}`",
        f"- E_kin positive: `{checks['ekin_positive']}`",
        f"- E_kin decreases with a: `{checks['ekin_decreases_with_a']}`",
        f"- scaled values approach Bessel lambdas: `{checks['scaled_values_approach_bessel']}`",
        "",
        "## Tables Summary",
        "",
        "- `bessel_anchor_spectra.csv` stores individual TB levels, Bessel references, residuals, scaled values, and degeneracy groups.",
        "- `bessel_anchor_fit.csv` stores individual-level and group-averaged residual power-law fits.",
        "- No plots were generated; tables are sufficient for this sprint.",
        "",
        "## Residual Magnitude Decrease",
        "",
        *_residual_decrease_lines(result["spectra_rows"]),
        "",
        "## Power-Law Fit Stability",
        "",
        *_fit_summary_lines(result["fit_rows"]),
        "",
        "## Final Verdict",
        "",
        f"`{result['verdict']}`",
        "",
        "Reasons:",
        "",
        *[f"- {reason}" for reason in result["verdict_reasons"]],
        "",
        "This verdict applies only to the circle Bessel anchor. It is not a positive",
        "Path B article result and does not authorize full shape comparison by itself.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the Bessel-anchor sprint and write requested outputs."""
    result = run_bessel_anchor()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "bessel_anchor_spectra.csv", result["spectra_rows"], SPECTRA_COLUMNS)
    write_csv(OUTPUT_DIR / "bessel_anchor_fit.csv", result["fit_rows"], FIT_COLUMNS)
    write_summary(OUTPUT_DIR / "bessel_anchor_summary.md", result)
    print(f"verdict: {result['verdict']}")
    for reason in result["verdict_reasons"]:
        print(f"reason: {reason}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

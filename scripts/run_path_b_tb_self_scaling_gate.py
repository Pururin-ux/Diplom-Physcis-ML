"""Run the TB-only self-scaling gate for Article Path B."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.path_b_tb_self_scaling import (  # noqa: E402
    ASPECT_RATIO,
    N2_BESSEL_GROUND,
    N_VALUES,
    SIZES,
    baseline_rows,
    fit_models,
    fit_rows_for_csv,
    spectra_rows,
    summarize_gate,
)


OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_path_b_tb_continuum_scaling"
BESSEL_ANCHOR_PATH = OUTPUT_DIR / "bessel_anchor_spectra.csv"

SPECTRA_COLUMNS = [
    "n",
    "rAR",
    "a",
    "E0_TB",
    "Ekin0_TB",
    "Y_a2E",
    "N_sites",
    "N_boundary_sites",
    "boundary_fraction",
    "A_continuum",
    "P_continuum",
    "area_pixelation_proxy",
    "boundary_pixelation_proxy",
]

FIT_COLUMNS = [
    "n",
    "model",
    "lambda_TB_inf",
    "lambda_rel_error_vs_bessel_if_n2",
    "delta_if_available",
    "p_TB_if_available",
    "c1_if_available",
    "c2_if_available",
    "RMSE",
    "R2",
    "AIC_or_BIC_if_available",
    "leave_one_size_out_stability",
    "model_notes",
]

BASELINE_COLUMNS = [
    "n",
    "a",
    "residual_after_effective_radius",
    "residual_after_boundary_fraction",
    "residual_after_best_simple_baseline",
    "N_sites",
    "N_boundary_sites",
    "boundary_fraction",
    "P_continuum",
    "A_continuum",
    "area_pixelation_proxy",
    "boundary_pixelation_proxy",
    "best_baseline_name",
    "best_baseline_R2",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write CSV rows with stable columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def load_bessel_anchor_ground(path: Path = BESSEL_ANCHOR_PATH) -> dict[float, float]:
    """Load existing n=2.0 Bessel-anchor TB ground states, if present."""
    if not path.exists():
        return {}
    out: dict[float, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["level_index"]) == 0:
                out[float(row["a"])] = float(row["E_TB"])
    return out


def _format_map(values: dict[float, object]) -> str:
    """Format n-keyed dictionaries for Markdown."""
    return ", ".join(f"n={n_value}: `{values[n_value]}`" for n_value in sorted(values))


def write_summary(path: Path, metadata: dict[str, object]) -> None:
    """Write the TB self-scaling gate summary."""
    n2_errors = metadata["n2_errors"]
    feature_models = metadata["feature_models"]
    lambda_by_n = metadata["lambda_by_n_effective_radius"]
    delta_by_n = metadata["delta_by_n"]
    p_values = metadata["p_values"]
    lines = [
        "# TB Self-Scaling Gate Summary",
        "",
        "## Scope",
        "",
        "This is a TB-only self-consistent finite-size scaling gate for Article",
        "Path B after the embedded-mask FD reference failed the N501 convergence",
        "gate. It uses direct tight-binding ground-state values and geometric",
        "diagnostics only.",
        "",
        "No FD reference was used. No FD reference values were loaded. No TB-vs-FD",
        "residuals were computed. Shape contrast against FD remains blocked.",
        "",
        "The analysis does not use ML, Q, or S objectives.",
        "",
        "## Tested Domain",
        "",
        f"- rAR: `{ASPECT_RATIO}`",
        f"- n values: `{N_VALUES}`",
        f"- sizes: `{SIZES}`",
        "- verdict is based on the ground state only",
        "",
        "## n=2.0 Bessel Calibration",
        "",
        f"- exact disk ground value `j01^2`: `{N2_BESSEL_GROUND}`",
        *[f"- {model}: relative error `{error}`" for model, error in sorted(n2_errors.items())],
        f"- best n=2.0 relative error: `{metadata['n2_best_error']}`",
        f"- n=2.0 model-to-model lambda spread / Bessel: `{metadata['n2_lambda_spread_relative']}`",
        f"- calibration accepted: `{metadata['calibration_ok']}`",
        "",
        "## Fitted Ground-State Parameters",
        "",
        f"- effective-radius lambda_TB_inf by n: {_format_map(lambda_by_n)}",
        f"- effective-radius delta_n by n: {_format_map(delta_by_n)}",
        f"- power-law p_TB(n): {_format_map(p_values)}",
        f"- power-law LOO stability accepted for all n: `{metadata['p_stable']}`",
        "",
        "Important interpretation: `lambda_TB_inf(n)` depending on `n` is ordinary",
        "shape dependence of continuum-like eigenvalues. It is not treated as a",
        "novel Path B signal.",
        "",
        "## Effective-Radius Baseline",
        "",
        f"- killed signal: `{metadata['effective_radius_kills']}`",
        "- criterion: high per-n fit quality and no systematic residual structure",
        "  large enough to justify downstream continuum-reference repair",
        "",
        "## Boundary-Fraction Baseline",
        "",
        f"- R2: `{metadata['boundary_fraction_r2']}`",
        f"- leave-one-row-out R2: `{metadata['boundary_fraction_loo_r2']}`",
        f"- max absolute mean residual by n after baseline: `{metadata['boundary_fraction_max_abs_mean_by_n']}`",
        f"- killed signal: `{metadata['boundary_fraction_kills']}`",
        "",
        "## Pixelation / Geometry Baselines",
        "",
        f"- best simple baseline: `{metadata['best_baseline_name']}`",
        f"- best simple baseline R2: `{metadata['best_baseline_r2']}`",
        f"- best simple baseline leave-one-row-out R2: `{metadata['best_baseline_loo_r2']}`",
        f"- best simple baseline max absolute mean residual by n: `{metadata['best_baseline_max_abs_mean_by_n']}`",
        f"- killed signal: `{metadata['pixelation_kills']}`",
        "",
        "Feature baseline diagnostics:",
        "",
        *[
            f"- {name}: R2=`{details['r2']}`, LOO_R2=`{details['loo_r2']}`"
            for name, details in sorted(feature_models.items())
        ],
        "",
        "## Surviving Signal",
        "",
        f"- TB self-scaling survives minimal gate: `{metadata['verdict'] == 'TB_SELF_SCALING_SURVIVES_MINIMAL_GATE'}`",
        "",
        "## Final Verdict",
        "",
        f"`{metadata['verdict']}`",
        "",
        "If this verdict is killed or inconclusive, Path B should be closed or",
        "reframed as a negative benchmark / baseline-first audit. Shortley-Weller",
        "or cut-cell FD repair is not recommended unless the TB self-scaling signal",
        "survives this minimal gate.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the TB self-scaling gate and write reports."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    anchor_ground = load_bessel_anchor_ground()
    rows = spectra_rows(anchor_ground)
    fits = fit_models(rows)
    baseline_csv_rows, baseline_metadata = baseline_rows(rows, fits)
    metadata = summarize_gate(rows, fits, baseline_metadata)

    write_csv(OUTPUT_DIR / "tb_self_scaling_spectra.csv", rows, SPECTRA_COLUMNS)
    write_csv(OUTPUT_DIR / "tb_self_scaling_fits.csv", fit_rows_for_csv(fits), FIT_COLUMNS)
    write_csv(OUTPUT_DIR / "tb_self_scaling_baselines.csv", baseline_csv_rows, BASELINE_COLUMNS)
    write_summary(OUTPUT_DIR / "tb_self_scaling_summary.md", metadata)

    print(f"verdict: {metadata['verdict']}")
    print(f"n2_best_error: {metadata['n2_best_error']}")
    print(f"lambda_by_n_effective_radius: {metadata['lambda_by_n_effective_radius']}")
    print(f"delta_by_n: {metadata['delta_by_n']}")
    print(f"p_values: {metadata['p_values']}")
    print(f"effective_radius_kills: {metadata['effective_radius_kills']}")
    print(f"boundary_fraction_kills: {metadata['boundary_fraction_kills']}")
    print(f"pixelation_kills: {metadata['pixelation_kills']}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

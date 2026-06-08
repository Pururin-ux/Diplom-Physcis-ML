"""Run the FD N=501 convergence gate for Article Path B."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.path_b_fd_reference import (  # noqa: E402
    ASPECT_RATIO,
    FD501_CONSISTENCY_TRIPLE,
    FD501_NEW_GRID_VALUES,
    FD501_PRIMARY_TRIPLE,
    N_LEVELS,
    N_VALUES,
    add_grid_source,
    estimate_order_rows,
    first_bessel_disk_levels,
    grid_convergence_rows,
    reference_uncertainty,
    richardson_extrapolate,
)


OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_path_b_tb_continuum_scaling"
EXISTING_GRID_PATH = OUTPUT_DIR / "fd_reference_grid_convergence.csv"

CONVERGENCE_COLUMNS = [
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
    "source",
]

ORDER_COLUMNS = [
    "n",
    "rAR",
    "level_index",
    "triple",
    "method",
    "N_grid_1",
    "N_grid_2",
    "N_grid_3",
    "h1",
    "h2",
    "h3",
    "lambda1",
    "lambda2",
    "lambda3",
    "reference_lambda_if_available",
    "p_estimate",
    "p_status",
    "delta12",
    "delta23",
    "delta_ratio",
]

EXTRAPOLATION_COLUMNS = [
    "n",
    "rAR",
    "level_index",
    "model",
    "lambda_candidate",
    "p_used",
    "lambda_raw_251",
    "lambda_raw_501",
    "lambda_bessel_if_available",
    "abs_error_vs_bessel_if_available",
    "rel_error_vs_bessel_if_available",
    "used_for_uncertainty_true_false",
    "notes",
]

RECOMMENDED_COLUMNS = [
    "n",
    "rAR",
    "level_index",
    "lambda_recommended",
    "recommendation_model",
    "p_observed_primary",
    "p_observed_consistency",
    "reference_uncertainty_estimate",
    "relative_reference_uncertainty",
    "validation_status",
    "downstream_use_allowed_true_false",
]


def read_csv_rows(path: Path) -> list[dict[str, object]]:
    """Read CSV rows into dictionaries."""
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write CSV rows with stable columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _row(
    rows: list[dict[str, object]],
    n_value: float,
    n_grid: int,
    level_index: int,
) -> dict[str, object]:
    """Return one convergence row."""
    matches = [
        item
        for item in rows
        if np.isclose(float(item["n"]), float(n_value))
        and int(item["N_grid"]) == int(n_grid)
        and int(item["level_index"]) == int(level_index)
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for n={n_value}, N={n_grid}, level={level_index}; got {len(matches)}.")
    return matches[0]


def _p_value(
    order_rows: list[dict[str, object]],
    n_value: float,
    level_index: int,
    triple: str,
    method: str,
) -> float | None:
    """Return an order estimate or None."""
    matches = [
        item
        for item in order_rows
        if np.isclose(float(item["n"]), float(n_value))
        and int(item["level_index"]) == int(level_index)
        and str(item["triple"]) == triple
        and str(item["method"]) == method
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one p row for n={n_value}, level={level_index}, {triple}, {method}.")
    value = matches[0]["p_estimate"]
    return None if value == "" else float(value)


def _bessel_value(level_index: int) -> float:
    """Return exact Bessel value for a disk level."""
    return first_bessel_disk_levels(N_LEVELS)[int(level_index)].lambda_value


def merge_existing_and_new_rows() -> list[dict[str, object]]:
    """Load existing FD rows and compute the new N=126 and N=501 rows."""
    if EXISTING_GRID_PATH.exists():
        existing_rows = read_csv_rows(EXISTING_GRID_PATH)
    else:
        existing_rows = grid_convergence_rows()
    new_rows = grid_convergence_rows(grid_values=FD501_NEW_GRID_VALUES)
    combined = add_grid_source([*existing_rows, *new_rows])
    combined.sort(key=lambda item: (float(item["n"]), int(item["N_grid"]), int(item["level_index"])))
    return combined


def make_extrapolation_rows(
    convergence_rows: list[dict[str, object]],
    order_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Build raw and extrapolated reference-candidate rows."""
    out: list[dict[str, object]] = []
    for n_value in N_VALUES:
        for level_index in range(N_LEVELS):
            row251 = _row(convergence_rows, n_value, 251, level_index)
            row501 = _row(convergence_rows, n_value, 501, level_index)
            lambda251 = float(row251["lambda_fd_unit"])
            lambda501 = float(row501["lambda_fd_unit"])
            h251 = float(row251["h"])
            h501 = float(row501["h"])
            bessel = _bessel_value(level_index) if np.isclose(n_value, 2.0) else ""
            p_method = "bessel_error" if np.isclose(n_value, 2.0) else "self_convergence"
            p_observed = _p_value(order_rows, n_value, level_index, "primary_126_251_501", p_method)
            candidates: list[tuple[str, float, str, bool, str]] = [
                ("raw_N501", lambda501, "", True, "raw finest-grid FD value"),
                ("richardson_p1", richardson_extrapolate(lambda251, lambda501, h251, h501, 1.0), "1.0", True, ""),
                ("richardson_p2", richardson_extrapolate(lambda251, lambda501, h251, h501, 2.0), "2.0", True, ""),
            ]
            if p_observed is not None:
                candidates.append(
                    (
                        "richardson_observed_p",
                        richardson_extrapolate(lambda251, lambda501, h251, h501, p_observed),
                        str(p_observed),
                        True,
                        "primary triple observed p",
                    )
                )
            else:
                candidates.append(("richardson_observed_p", float("nan"), "", False, "observed p not found"))

            for model, candidate, p_used, used, notes in candidates:
                abs_error = "" if bessel == "" or not np.isfinite(candidate) else abs(float(candidate) - float(bessel))
                rel_error = "" if bessel == "" or not np.isfinite(candidate) else abs(float(candidate) - float(bessel)) / float(bessel)
                out.append(
                    {
                        "n": float(n_value),
                        "rAR": ASPECT_RATIO,
                        "level_index": int(level_index),
                        "model": model,
                        "lambda_candidate": candidate,
                        "p_used": p_used,
                        "lambda_raw_251": lambda251,
                        "lambda_raw_501": lambda501,
                        "lambda_bessel_if_available": bessel,
                        "abs_error_vs_bessel_if_available": abs_error,
                        "rel_error_vs_bessel_if_available": rel_error,
                        "used_for_uncertainty_true_false": bool(used),
                        "notes": notes,
                    }
                )
    return out


def _candidate_values_for_uncertainty(extrapolation_rows: list[dict[str, object]], n_value: float, level_index: int) -> list[float]:
    """Return plausible finite candidates for uncertainty spread."""
    values: list[float] = []
    for item in extrapolation_rows:
        if not np.isclose(float(item["n"]), float(n_value)) or int(item["level_index"]) != int(level_index):
            continue
        if str(item["used_for_uncertainty_true_false"]) != "True" and item["used_for_uncertainty_true_false"] is not True:
            continue
        value = float(item["lambda_candidate"])
        if np.isfinite(value):
            values.append(value)
    return values


def _candidate_value(extrapolation_rows: list[dict[str, object]], n_value: float, level_index: int, model: str) -> float:
    """Return one extrapolation candidate."""
    matches = [
        item
        for item in extrapolation_rows
        if np.isclose(float(item["n"]), float(n_value))
        and int(item["level_index"]) == int(level_index)
        and str(item["model"]) == model
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one candidate for n={n_value}, level={level_index}, model={model}.")
    return float(matches[0]["lambda_candidate"])


def _raw_values(extrapolation_rows: list[dict[str, object]], n_value: float, level_index: int) -> tuple[float, float]:
    """Return raw N=251 and N=501 values for one level."""
    matches = [
        item
        for item in extrapolation_rows
        if np.isclose(float(item["n"]), float(n_value))
        and int(item["level_index"]) == int(level_index)
        and str(item["model"]) == "raw_N501"
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one raw row for n={n_value}, level={level_index}.")
    return float(matches[0]["lambda_raw_251"]), float(matches[0]["lambda_raw_501"])


def make_recommended_rows(
    extrapolation_rows: list[dict[str, object]],
    order_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Choose downstream references and classify the FD convergence gate."""
    n2_p0 = _p_value(order_rows, 2.0, 0, "primary_126_251_501", "bessel_error")
    n12_p0 = _p_value(order_rows, 1.2, 0, "primary_126_251_501", "self_convergence")
    n4_p0 = _p_value(order_rows, 4.0, 0, "primary_126_251_501", "self_convergence")
    n12_p0_consistency = _p_value(order_rows, 1.2, 0, "consistency_151_201_251", "self_convergence")
    n4_p0_consistency = _p_value(order_rows, 4.0, 0, "consistency_151_201_251", "self_convergence")

    # Use raw N=501 as the conservative denominator for the hard uncertainty
    # gate. If the gate passes, downstream rows may still select observed-p
    # extrapolation; if it fails, no noncircle reference is authorized.
    n12_reference = _candidate_value(extrapolation_rows, 1.2, 0, "raw_N501")
    n4_reference = _candidate_value(extrapolation_rows, 4.0, 0, "raw_N501")

    n12_uncertainty, n12_relative = reference_uncertainty(
        _candidate_values_for_uncertainty(extrapolation_rows, 1.2, 0),
        n12_reference,
    )
    n4_uncertainty, n4_relative = reference_uncertainty(
        _candidate_values_for_uncertainty(extrapolation_rows, 4.0, 0),
        n4_reference,
    )

    n2_raw251, n2_validates = _raw_values(extrapolation_rows, 2.0, 0)
    n2_bessel = _bessel_value(0)
    n2_rel_501 = abs(n2_validates - n2_bessel) / n2_bessel
    n2_rel_251 = abs(n2_raw251 - n2_bessel) / n2_bessel
    circle_ok = n2_rel_501 < 0.0052206740942014095 and n2_p0 is not None

    shape_risk = False
    risk_reasons: list[str] = []
    if n2_p0 is not None and n12_p0 is not None and n12_p0 < 0.75 * n2_p0:
        shape_risk = True
        risk_reasons.append("p(n=1.2) is much lower than p(n=2.0)")
    if n12_p0 is None or n12_p0_consistency is None or abs(n12_p0 - n12_p0_consistency) > 0.5:
        shape_risk = True
        risk_reasons.append("p(n=1.2) is unstable between primary and consistency triples")
    if n12_relative >= 0.001:
        shape_risk = True
        risk_reasons.append("n=1.2 reference uncertainty is too large for downstream TB residual analysis")

    n12_gate_passed = n12_relative < 0.001
    n4_gate_passed = n4_relative < 0.001
    if not n4_gate_passed:
        risk_reasons.append("n=4.0 reference uncertainty requires downstream qualification")

    if not circle_ok:
        verdict = "FD_501_CONVERGENCE_FAILED"
    elif not n12_gate_passed or shape_risk or not n4_gate_passed:
        verdict = "FD_501_CONVERGENCE_INCONCLUSIVE"
    else:
        verdict = "FD_501_CONVERGENCE_PASSED"

    final_model = (
        "BESSEL_FOR_N2_AND_OBSERVED_P_FOR_NONCIRCLE"
        if verdict == "FD_501_CONVERGENCE_PASSED"
        else "FD_REFERENCE_INSUFFICIENT_FOR_SHAPE_CONTRAST"
    )

    recommended_rows: list[dict[str, object]] = []
    for n_value in N_VALUES:
        for level_index in range(N_LEVELS):
            p_method = "bessel_error" if np.isclose(n_value, 2.0) else "self_convergence"
            primary_p = _p_value(order_rows, n_value, level_index, "primary_126_251_501", p_method)
            consistency_p = _p_value(order_rows, n_value, level_index, "consistency_151_201_251", p_method)
            if np.isclose(n_value, 2.0):
                lambda_recommended = _bessel_value(level_index)
                uncertainty = 0.0
                relative = 0.0
                downstream = True
                status = "bessel_exact_reference"
            else:
                observed_candidate = _candidate_value(extrapolation_rows, n_value, level_index, "richardson_observed_p")
                lambda_recommended = (
                    observed_candidate
                    if verdict == "FD_501_CONVERGENCE_PASSED" and np.isfinite(observed_candidate)
                    else _candidate_value(extrapolation_rows, n_value, level_index, "raw_N501")
                )
                uncertainty, relative = reference_uncertainty(
                    _candidate_values_for_uncertainty(extrapolation_rows, n_value, level_index),
                    lambda_recommended,
                )
                downstream = bool(verdict == "FD_501_CONVERGENCE_PASSED" and relative < 0.001)
                status = "selected" if downstream else "insufficient_for_unqualified_shape_contrast"
            recommended_rows.append(
                {
                    "n": float(n_value),
                    "rAR": ASPECT_RATIO,
                    "level_index": int(level_index),
                    "lambda_recommended": lambda_recommended,
                    "recommendation_model": final_model if not np.isclose(n_value, 2.0) else "BESSEL_FOR_N2_AND_OBSERVED_P_FOR_NONCIRCLE",
                    "p_observed_primary": "" if primary_p is None else primary_p,
                    "p_observed_consistency": "" if consistency_p is None else consistency_p,
                    "reference_uncertainty_estimate": uncertainty,
                    "relative_reference_uncertainty": relative,
                    "validation_status": status,
                    "downstream_use_allowed_true_false": downstream,
                }
            )

    metadata = {
        "verdict": verdict,
        "circle_ok": circle_ok,
        "n2_ground_p": n2_p0,
        "n12_ground_p": n12_p0,
        "n4_ground_p": n4_p0,
        "n12_ground_p_consistency": n12_p0_consistency,
        "n4_ground_p_consistency": n4_p0_consistency,
        "n12_uncertainty": n12_uncertainty,
        "n12_relative_uncertainty": n12_relative,
        "n4_uncertainty": n4_uncertainty,
        "n4_relative_uncertainty": n4_relative,
        "n12_gate_passed": n12_gate_passed,
        "n4_gate_passed": n4_gate_passed,
        "shape_dependent_error_risk": shape_risk,
        "risk_reasons": risk_reasons,
        "recommended_model": final_model,
        "shape_contrast_allowed": verdict == "FD_501_CONVERGENCE_PASSED",
        "n2_ground_rel_error_raw_251": n2_rel_251,
        "n2_ground_rel_error_raw_501": n2_rel_501,
    }
    return recommended_rows, metadata


def _ground_summary_line(label: str, value: object) -> str:
    """Format one summary bullet."""
    return f"- {label}: `{value}`"


def write_summary(
    path: Path,
    metadata: dict[str, object],
) -> None:
    """Write the FD N=501 convergence summary."""
    risk_reasons = metadata["risk_reasons"] or ["none"]
    lines = [
        "# FD N501 Convergence Gate Summary",
        "",
        "## Scope",
        "",
        "This is an FD-only asymptotic convergence check for the Article Path B",
        "continuum reference. It does not run tight-binding spectra, does not run",
        "shape contrast, does not fit an effective-radius delta, does not use ML,",
        "and does not use Q or S objectives.",
        "",
        "## Why N_grid=501 Was Added",
        "",
        "The previous selected FD reference used `N_grid=251`, where the circle",
        "ground-state FD-vs-Bessel relative error was about `0.52%`. Before using",
        "FD references for TB residual analysis, this check adds a near-geometric",
        "refinement triple `N_grid={126,251,501}` so observed convergence order and",
        "reference uncertainty can be measured directly.",
        "",
        "## Why N_grid=301 Was Not Used",
        "",
        "`N_grid=301` does not complete the intended h-halving test around the",
        "existing `N_grid=251` reference. The chosen `126,251,501` sequence gives",
        "approximately `h={0.016,0.008,0.004}` and directly tests whether the",
        "finest existing reference behaves consistently under near-geometric",
        "refinement.",
        "",
        "## Grid Triples",
        "",
        f"- primary refinement triple: `{FD501_PRIMARY_TRIPLE}`",
        f"- existing-grid consistency triple: `{FD501_CONSISTENCY_TRIPLE}`",
        "",
        "All p estimates use the general unequal-step equation solved with",
        "`scipy.optimize.brentq`. The simple `log2(Delta12/Delta23)` shortcut is",
        "not used.",
        "",
        "## Ground-State Observed Orders",
        "",
        _ground_summary_line("n=2.0 Bessel-error p, primary triple", metadata["n2_ground_p"]),
        _ground_summary_line("n=1.2 self-convergence p, primary triple", metadata["n12_ground_p"]),
        _ground_summary_line("n=4.0 self-convergence p, primary triple", metadata["n4_ground_p"]),
        _ground_summary_line("n=1.2 self-convergence p, consistency triple", metadata["n12_ground_p_consistency"]),
        _ground_summary_line("n=4.0 self-convergence p, consistency triple", metadata["n4_ground_p_consistency"]),
        "",
        "The p estimates should be interpreted as observed numerical behavior of",
        "the embedded-mask FD discretization. For `n=1.2`, the domain is treated",
        "as a convex superellipse with singular/high-curvature boundary regions,",
        "not as a reentrant-corner domain.",
        "",
        "## Extrapolation and Reference Uncertainty",
        "",
        _ground_summary_line("n=2.0 raw N501 ground relative error vs Bessel", metadata["n2_ground_rel_error_raw_501"]),
        _ground_summary_line("n=1.2 level-0 reference uncertainty", metadata["n12_uncertainty"]),
        _ground_summary_line("n=1.2 level-0 relative reference uncertainty", metadata["n12_relative_uncertainty"]),
        _ground_summary_line("n=4.0 level-0 reference uncertainty", metadata["n4_uncertainty"]),
        _ground_summary_line("n=4.0 level-0 relative reference uncertainty", metadata["n4_relative_uncertainty"]),
        "",
        "Hard gate:",
        "",
        _ground_summary_line("relative_reference_uncertainty(n=1.2, level 0) < 0.001", metadata["n12_gate_passed"]),
        _ground_summary_line("relative_reference_uncertainty(n=4.0, level 0) < 0.001", metadata["n4_gate_passed"]),
        "",
        "## Shape-Dependent FD Error Risk",
        "",
        _ground_summary_line("FD_REFERENCE_SHAPE_DEPENDENT_ERROR_RISK", metadata["shape_dependent_error_risk"]),
        "",
        "Risk reasons:",
        "",
        *[f"- {reason}" for reason in risk_reasons],
        "",
        "## Recommended Reference Model",
        "",
        _ground_summary_line("recommended reference model", metadata["recommended_model"]),
        _ground_summary_line("minimal shape contrast allowed next", metadata["shape_contrast_allowed"]),
        "",
        "If the verdict is not `FD_501_CONVERGENCE_PASSED`, do not run shape",
        "contrast. Recommended alternatives are higher `N_grid`, a better boundary",
        "treatment, an alternative continuum solver, or removing `n=1.2` as a",
        "primary shape.",
        "",
        "## Final Verdict",
        "",
        f"`{metadata['verdict']}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the FD N=501 convergence gate and write outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convergence_rows = merge_existing_and_new_rows()
    order_rows = estimate_order_rows(convergence_rows)
    extrapolation_rows = make_extrapolation_rows(convergence_rows, order_rows)
    recommended_rows, metadata = make_recommended_rows(extrapolation_rows, order_rows)

    write_csv(OUTPUT_DIR / "fd_reference_501_convergence.csv", convergence_rows, CONVERGENCE_COLUMNS)
    write_csv(OUTPUT_DIR / "fd_reference_501_orders.csv", order_rows, ORDER_COLUMNS)
    write_csv(OUTPUT_DIR / "fd_reference_501_extrapolation_models.csv", extrapolation_rows, EXTRAPOLATION_COLUMNS)
    write_csv(OUTPUT_DIR / "fd_reference_501_recommended_values.csv", recommended_rows, RECOMMENDED_COLUMNS)
    write_summary(OUTPUT_DIR / "fd_reference_501_convergence_summary.md", metadata)

    print(f"verdict: {metadata['verdict']}")
    print(f"n2_ground_p: {metadata['n2_ground_p']}")
    print(f"n12_ground_p: {metadata['n12_ground_p']}")
    print(f"n4_ground_p: {metadata['n4_ground_p']}")
    print(f"n12_relative_uncertainty: {metadata['n12_relative_uncertainty']}")
    print(f"n4_relative_uncertainty: {metadata['n4_relative_uncertainty']}")
    print(f"shape_dependent_error_risk: {metadata['shape_dependent_error_risk']}")
    print(f"shape_contrast_allowed: {metadata['shape_contrast_allowed']}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

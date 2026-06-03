"""TB-only self-scaling gate for Article Path B after FD reference failure.

This module intentionally does not load or use finite-difference reference
values. It tests whether square-lattice tight-binding ground-state finite-size
scaling leaves any signal after effective-radius, boundary-fraction, and
simple geometry/pixelation baselines.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import curve_fit
from scipy.sparse.linalg import ArpackNoConvergence, eigsh
from scipy.special import gamma, jn_zeros

from .geometry import build_superellipse_dot
from .kwant_solver import _as_sorted_real_finite


N_VALUES = (1.2, 2.0, 4.0)
ASPECT_RATIO = 1.0
SIZES = (24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0)
N2_BESSEL_GROUND = float(jn_zeros(0, 1)[0] ** 2)
BOUNDARY_BASELINE_R2_GATE = 0.80


@dataclass(frozen=True)
class FitResult:
    """Fitted model parameters and diagnostics for one n value."""

    n: float
    model: str
    lambda_tb_inf: float
    delta: float | None
    p_tb: float | None
    c1: float | None
    c2: float | None
    rmse: float
    r2: float
    aic: float
    loo_stability: str
    predictions: np.ndarray
    notes: str


def site_coordinates(a_value: float, n_value: float, aspect_ratio: float = ASPECT_RATIO) -> set[tuple[int, int]]:
    """Return realized integer lattice coordinates for one superellipse dot."""
    fsys = build_superellipse_dot(a=float(a_value), b=float(a_value) * float(aspect_ratio), n=float(n_value))
    return {(int(site.tag[0]), int(site.tag[1])) for site in fsys.sites}


def count_boundary_sites(coords: set[tuple[int, int]]) -> int:
    """Count included sites with at least one nearest neighbor outside."""
    count = 0
    for x_value, y_value in coords:
        for neighbor in ((x_value - 1, y_value), (x_value + 1, y_value), (x_value, y_value - 1), (x_value, y_value + 1)):
            if neighbor not in coords:
                count += 1
                break
    return count


def continuum_area(a_value: float, n_value: float, aspect_ratio: float = ASPECT_RATIO) -> float:
    """Return continuum superellipse area in lattice-site units."""
    a_float = float(a_value)
    b_float = a_float * float(aspect_ratio)
    n_float = float(n_value)
    return float(4.0 * a_float * b_float * (gamma(1.0 + 1.0 / n_float) ** 2) / gamma(1.0 + 2.0 / n_float))


def continuum_perimeter(a_value: float, n_value: float, aspect_ratio: float = ASPECT_RATIO, samples: int = 20000) -> float:
    """Return a polyline approximation to the continuum superellipse perimeter."""
    if int(samples) < 1000:
        raise ValueError("samples must be at least 1000 for perimeter approximation.")
    a_float = float(a_value)
    b_float = a_float * float(aspect_ratio)
    exponent = 2.0 / float(n_value)
    theta = np.linspace(0.0, 2.0 * pi, int(samples), endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    x_values = a_float * np.sign(cos_t) * np.abs(cos_t) ** exponent
    y_values = b_float * np.sign(sin_t) * np.abs(sin_t) ** exponent
    dx = np.diff(np.r_[x_values, x_values[0]])
    dy = np.diff(np.r_[y_values, y_values[0]])
    return float(np.sum(np.sqrt(dx * dx + dy * dy)))


def geometry_diagnostics(a_value: float, n_value: float, aspect_ratio: float = ASPECT_RATIO) -> dict[str, float]:
    """Return realized geometry and continuum/pixelation diagnostics."""
    coords = site_coordinates(float(a_value), float(n_value), float(aspect_ratio))
    n_sites = len(coords)
    n_boundary = count_boundary_sites(coords)
    area = continuum_area(float(a_value), float(n_value), float(aspect_ratio))
    perimeter = continuum_perimeter(float(a_value), float(n_value), float(aspect_ratio))
    return {
        "N_sites": float(n_sites),
        "N_boundary_sites": float(n_boundary),
        "boundary_fraction": float(n_boundary / n_sites),
        "A_continuum": area,
        "P_continuum": perimeter,
        "area_pixelation_proxy": abs(float(n_sites) - area) / area,
        "boundary_pixelation_proxy": abs(float(n_boundary) - perimeter) / perimeter,
    }


def low_tb_levels(a_value: float, n_value: float, aspect_ratio: float = ASPECT_RATIO, n_levels: int = 1) -> np.ndarray:
    """Compute the lowest tight-binding eigenvalues for one superellipse dot."""
    fsys = build_superellipse_dot(a=float(a_value), b=float(a_value) * float(aspect_ratio), n=float(n_value))
    n_sites = len(fsys.sites)
    hamiltonian = fsys.hamiltonian_submatrix(sparse=True).tocsr()
    if n_sites <= n_levels + 1:
        values = np.linalg.eigvalsh(hamiltonian.toarray())
    else:
        solve_k = min(n_sites - 1, max(2 * int(n_levels), 12))
        try:
            values, _ = eigsh(
                hamiltonian,
                k=solve_k,
                which="SA",
                tol=1e-11,
                ncv=max(4 * solve_k + 20, 80),
                maxiter=max(1000, 20 * n_sites),
            )
        except ArpackNoConvergence:
            values, _ = eigsh(
                hamiltonian,
                k=solve_k,
                sigma=-4.0,
                which="LM",
                tol=1e-11,
                ncv=max(4 * solve_k + 20, 80),
                maxiter=max(1000, 20 * n_sites),
            )
    sorted_values = _as_sorted_real_finite(values)
    if sorted_values.shape[0] < n_levels:
        raise ValueError(f"Expected at least {n_levels} eigenvalues, got {sorted_values.shape[0]}.")
    return sorted_values[:n_levels]


def spectra_rows(
    bessel_anchor_ground: dict[float, float] | None = None,
    n_values: Sequence[float] = N_VALUES,
    sizes: Sequence[float] = SIZES,
) -> list[dict[str, object]]:
    """Compute or reuse TB ground-state rows and add geometry diagnostics."""
    bessel_anchor_ground = bessel_anchor_ground or {}
    rows: list[dict[str, object]] = []
    for n_value in n_values:
        for a_value in sizes:
            if np.isclose(float(n_value), 2.0) and float(a_value) in bessel_anchor_ground:
                e0 = float(bessel_anchor_ground[float(a_value)])
            else:
                e0 = float(low_tb_levels(float(a_value), float(n_value), ASPECT_RATIO, n_levels=1)[0])
            ekin = e0 + 4.0
            diagnostics = geometry_diagnostics(float(a_value), float(n_value), ASPECT_RATIO)
            rows.append(
                {
                    "n": float(n_value),
                    "rAR": ASPECT_RATIO,
                    "a": float(a_value),
                    "E0_TB": e0,
                    "Ekin0_TB": ekin,
                    "Y_a2E": (float(a_value) ** 2) * ekin,
                    **diagnostics,
                }
            )
    return rows


def _fit_diagnostics(y_true: np.ndarray, y_pred: np.ndarray, k_params: int) -> tuple[float, float, float]:
    """Return RMSE, R2, and AIC for a fitted model."""
    residual = y_true - y_pred
    sse = float(np.sum(residual * residual))
    rmse = float(sqrt(float(np.mean(residual * residual))))
    ss_tot = float(np.sum((y_true - float(np.mean(y_true))) ** 2))
    r2 = 1.0 if ss_tot == 0.0 and sse == 0.0 else 1.0 - sse / ss_tot if ss_tot > 0.0 else float("nan")
    aic = float(len(y_true) * np.log(max(sse / len(y_true), 1e-300)) + 2 * int(k_params))
    return rmse, r2, aic


def _linear_design_fit(a_values: np.ndarray, y_values: np.ndarray, powers: Sequence[int]) -> tuple[np.ndarray, np.ndarray]:
    """Fit y=lambda+sum c_i/a**power and return coefficients and predictions."""
    columns = [np.ones_like(a_values)]
    columns.extend(1.0 / np.power(a_values, int(power)) for power in powers)
    design = np.column_stack(columns)
    coefficients = np.linalg.lstsq(design, y_values, rcond=None)[0]
    return coefficients, design @ coefficients


def _power_model(a_values: np.ndarray, lambda_value: float, coefficient: float, p_value: float) -> np.ndarray:
    """Power-law finite-size model for scaled kinetic energy."""
    return lambda_value + coefficient / np.power(a_values, p_value)


def effective_radius_y(a_values: np.ndarray, lambda_value: float, delta_value: float) -> np.ndarray:
    """Return scaled Y=a**2*Ekin for the effective-radius model."""
    return lambda_value * (a_values * a_values) / np.power(a_values + delta_value, 2.0)


def fit_effective_radius(a_values: Sequence[float], y_values: Sequence[float]) -> tuple[float, float, np.ndarray]:
    """Fit the effective-radius model to scaled ground-state data."""
    a_arr = np.asarray(a_values, dtype=float)
    y_arr = np.asarray(y_values, dtype=float)
    lambda0 = float(y_arr[-1])
    params, _ = curve_fit(
        effective_radius_y,
        a_arr,
        y_arr,
        p0=(lambda0, 0.0),
        bounds=([0.0, -0.9 * float(np.min(a_arr))], [np.inf, 0.9 * float(np.min(a_arr))]),
        maxfev=100000,
    )
    prediction = effective_radius_y(a_arr, float(params[0]), float(params[1]))
    return float(params[0]), float(params[1]), prediction


def _fit_power_model(a_values: np.ndarray, y_values: np.ndarray) -> tuple[float, float, float, np.ndarray]:
    """Fit the nonlinear power-law model."""
    lambda0 = float(y_values[-1])
    coefficient0 = float((y_values[0] - y_values[-1]) * a_values[0])
    params, _ = curve_fit(
        _power_model,
        a_values,
        y_values,
        p0=(lambda0, coefficient0, 1.0),
        bounds=([0.0, -np.inf, 0.1], [np.inf, np.inf, 6.0]),
        maxfev=100000,
    )
    prediction = _power_model(a_values, float(params[0]), float(params[1]), float(params[2]))
    return float(params[0]), float(params[1]), float(params[2]), prediction


def _fit_power_summary(a_values: np.ndarray, y_values: np.ndarray) -> tuple[float, None, float]:
    """Return lambda and p for leave-one-size-out power-model stability."""
    lambda_value, _, p_value, _ = _fit_power_model(a_values, y_values)
    return lambda_value, None, p_value


def _fit_effective_radius_summary(a_values: np.ndarray, y_values: np.ndarray) -> tuple[float, float, None]:
    """Return lambda and delta for leave-one-size-out effective-radius stability."""
    lambda_value, delta_value, _ = fit_effective_radius(a_values, y_values)
    return lambda_value, delta_value, None


def _loo_stability(
    a_values: np.ndarray,
    y_values: np.ndarray,
    fit_lambda: Callable[[np.ndarray, np.ndarray], tuple[float, float | None, float | None]],
) -> str:
    """Return compact leave-one-size-out parameter stability text."""
    lambdas: list[float] = []
    deltas: list[float] = []
    powers: list[float] = []
    for leave_index in range(len(a_values)):
        mask = np.ones(len(a_values), dtype=bool)
        mask[leave_index] = False
        try:
            lambda_value, delta_value, p_value = fit_lambda(a_values[mask], y_values[mask])
        except (RuntimeError, ValueError, np.linalg.LinAlgError):
            continue
        lambdas.append(float(lambda_value))
        if delta_value is not None:
            deltas.append(float(delta_value))
        if p_value is not None:
            powers.append(float(p_value))
    if not lambdas:
        return "unstable_no_successful_loo_fits"
    lambda_range = max(lambdas) - min(lambdas)
    parts = [f"lambda_range={lambda_range:.6g}"]
    stable = lambda_range / max(abs(float(np.mean(lambdas))), 1e-12) < 0.02
    if deltas:
        parts.append(f"delta_range={max(deltas) - min(deltas):.6g}")
        stable = stable and (max(deltas) - min(deltas) < 2.0)
    if powers:
        parts.append(f"p_range={max(powers) - min(powers):.6g}")
        stable = stable and (max(powers) - min(powers) < 1.0)
    parts.append(f"stable={stable}")
    return "; ".join(parts)


def fit_models(rows: Sequence[dict[str, object]]) -> list[FitResult]:
    """Fit all primary self-scaling models for each n."""
    out: list[FitResult] = []
    for n_value in sorted({float(row["n"]) for row in rows}):
        selected = sorted([row for row in rows if np.isclose(float(row["n"]), n_value)], key=lambda row: float(row["a"]))
        a_values = np.array([float(row["a"]) for row in selected], dtype=float)
        y_values = np.array([float(row["Y_a2E"]) for row in selected], dtype=float)

        coeffs, pred = _linear_design_fit(a_values, y_values, powers=(1,))
        rmse, r2, aic = _fit_diagnostics(y_values, pred, k_params=2)
        out.append(
            FitResult(
                n=n_value,
                model="linear_inverse_size",
                lambda_tb_inf=float(coeffs[0]),
                delta=None,
                p_tb=None,
                c1=float(coeffs[1]),
                c2=None,
                rmse=rmse,
                r2=r2,
                aic=aic,
                loo_stability=_loo_stability(
                    a_values,
                    y_values,
                    lambda aa, yy: (float(_linear_design_fit(aa, yy, powers=(1,))[0][0]), None, None),
                ),
                predictions=pred,
                notes="Y=lambda+c1/a",
            )
        )

        coeffs, pred = _linear_design_fit(a_values, y_values, powers=(1, 2))
        rmse, r2, aic = _fit_diagnostics(y_values, pred, k_params=3)
        out.append(
            FitResult(
                n=n_value,
                model="quadratic_inverse_size",
                lambda_tb_inf=float(coeffs[0]),
                delta=None,
                p_tb=None,
                c1=float(coeffs[1]),
                c2=float(coeffs[2]),
                rmse=rmse,
                r2=r2,
                aic=aic,
                loo_stability=_loo_stability(
                    a_values,
                    y_values,
                    lambda aa, yy: (float(_linear_design_fit(aa, yy, powers=(1, 2))[0][0]), None, None),
                ),
                predictions=pred,
                notes="Y=lambda+c1/a+c2/a^2",
            )
        )

        lambda_power, coefficient, p_value, pred = _fit_power_model(a_values, y_values)
        rmse, r2, aic = _fit_diagnostics(y_values, pred, k_params=3)
        out.append(
            FitResult(
                n=n_value,
                model="power_law_residual",
                lambda_tb_inf=lambda_power,
                delta=None,
                p_tb=p_value,
                c1=coefficient,
                c2=None,
                rmse=rmse,
                r2=r2,
                aic=aic,
                loo_stability=_loo_stability(
                    a_values,
                    y_values,
                    _fit_power_summary,
                ),
                predictions=pred,
                notes="Y=lambda+C/a^p",
            )
        )

        lambda_eff, delta_eff, pred = fit_effective_radius(a_values, y_values)
        rmse, r2, aic = _fit_diagnostics(y_values, pred, k_params=2)
        out.append(
            FitResult(
                n=n_value,
                model="effective_radius",
                lambda_tb_inf=lambda_eff,
                delta=delta_eff,
                p_tb=None,
                c1=None,
                c2=None,
                rmse=rmse,
                r2=r2,
                aic=aic,
                loo_stability=_loo_stability(
                    a_values,
                    y_values,
                    _fit_effective_radius_summary,
                ),
                predictions=pred,
                notes="Ekin=lambda/(a+delta)^2",
            )
        )
    return out


def _fit_linear_feature(feature: np.ndarray, target: np.ndarray) -> tuple[float, float, np.ndarray, float, float]:
    """Fit target=intercept+slope*feature and return diagnostics."""
    design = np.column_stack([np.ones_like(feature), feature])
    intercept, slope = np.linalg.lstsq(design, target, rcond=None)[0]
    predicted = design @ np.array([intercept, slope])
    rmse, r2, _ = _fit_diagnostics(target, predicted, k_params=2)
    return float(intercept), float(slope), predicted, rmse, r2


def _loo_r2_linear_feature(feature: np.ndarray, target: np.ndarray) -> float:
    """Return leave-one-row-out predictive R2 for a single feature."""
    preds = np.empty_like(target)
    for index in range(len(target)):
        mask = np.ones(len(target), dtype=bool)
        mask[index] = False
        try:
            intercept, slope, _, _, _ = _fit_linear_feature(feature[mask], target[mask])
            preds[index] = intercept + slope * feature[index]
        except np.linalg.LinAlgError:
            preds[index] = np.mean(target[mask])
    ss_res = float(np.sum((target - preds) ** 2))
    ss_tot = float(np.sum((target - float(np.mean(target))) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")


def _mean_abs_group_residual_after_baseline(rows: Sequence[dict[str, object]], residuals: np.ndarray) -> float:
    """Return max absolute mean residual by n after a baseline."""
    by_n: list[float] = []
    for n_value in sorted({float(row["n"]) for row in rows}):
        values = [residuals[index] for index, row in enumerate(rows) if np.isclose(float(row["n"]), n_value)]
        by_n.append(abs(float(np.mean(values))))
    return max(by_n) if by_n else float("inf")


def baseline_rows(rows: Sequence[dict[str, object]], fits: Sequence[FitResult]) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Compute residuals after effective-radius and simple geometry baselines."""
    sorted_rows = sorted(rows, key=lambda row: (float(row["n"]), float(row["a"])))
    effective_predictions: dict[tuple[float, float], float] = {}
    for fit in fits:
        if fit.model != "effective_radius":
            continue
        fit_rows_for_n = sorted([row for row in sorted_rows if np.isclose(float(row["n"]), fit.n)], key=lambda row: float(row["a"]))
        for row, prediction in zip(fit_rows_for_n, fit.predictions):
            effective_predictions[(float(row["n"]), float(row["a"]))] = float(prediction)

    residual_eff = np.array(
        [
            float(row["Y_a2E"]) - effective_predictions[(float(row["n"]), float(row["a"]))]
            for row in sorted_rows
        ],
        dtype=float,
    )

    feature_names = (
        "N_sites",
        "N_boundary_sites",
        "boundary_fraction",
        "P_continuum",
        "A_continuum",
        "area_pixelation_proxy",
        "boundary_pixelation_proxy",
    )
    feature_models: dict[str, dict[str, object]] = {}
    for feature_name in feature_names:
        feature = np.array([float(row[feature_name]) for row in sorted_rows], dtype=float)
        intercept, slope, pred, rmse, r2 = _fit_linear_feature(feature, residual_eff)
        loo_r2 = _loo_r2_linear_feature(feature, residual_eff)
        feature_models[feature_name] = {
            "intercept": intercept,
            "slope": slope,
            "pred": pred,
            "rmse": rmse,
            "r2": r2,
            "loo_r2": loo_r2,
            "max_abs_mean_by_n": _mean_abs_group_residual_after_baseline(sorted_rows, residual_eff - pred),
        }

    best_name = max(feature_models, key=lambda name: float(feature_models[name]["r2"]))
    best_model = feature_models[best_name]
    boundary_model = feature_models["boundary_fraction"]
    out: list[dict[str, object]] = []
    for index, row in enumerate(sorted_rows):
        boundary_residual = float(residual_eff[index] - np.asarray(boundary_model["pred"])[index])
        best_residual = float(residual_eff[index] - np.asarray(best_model["pred"])[index])
        out.append(
            {
                "n": float(row["n"]),
                "a": float(row["a"]),
                "residual_after_effective_radius": float(residual_eff[index]),
                "residual_after_boundary_fraction": boundary_residual,
                "residual_after_best_simple_baseline": best_residual,
                "N_sites": float(row["N_sites"]),
                "N_boundary_sites": float(row["N_boundary_sites"]),
                "boundary_fraction": float(row["boundary_fraction"]),
                "P_continuum": float(row["P_continuum"]),
                "A_continuum": float(row["A_continuum"]),
                "area_pixelation_proxy": float(row["area_pixelation_proxy"]),
                "boundary_pixelation_proxy": float(row["boundary_pixelation_proxy"]),
                "best_baseline_name": best_name,
                "best_baseline_R2": float(best_model["r2"]),
            }
        )
    metadata = {
        "feature_models": feature_models,
        "best_baseline_name": best_name,
        "best_baseline_r2": float(best_model["r2"]),
        "best_baseline_loo_r2": float(best_model["loo_r2"]),
        "boundary_fraction_r2": float(boundary_model["r2"]),
        "boundary_fraction_loo_r2": float(boundary_model["loo_r2"]),
        "boundary_fraction_max_abs_mean_by_n": float(boundary_model["max_abs_mean_by_n"]),
        "best_baseline_max_abs_mean_by_n": float(best_model["max_abs_mean_by_n"]),
    }
    return out, metadata


def fit_rows_for_csv(fits: Sequence[FitResult]) -> list[dict[str, object]]:
    """Convert fit results to CSV rows."""
    rows: list[dict[str, object]] = []
    for fit in fits:
        rel_error = ""
        if np.isclose(fit.n, 2.0):
            rel_error = abs(float(fit.lambda_tb_inf) - N2_BESSEL_GROUND) / N2_BESSEL_GROUND
        rows.append(
            {
                "n": fit.n,
                "model": fit.model,
                "lambda_TB_inf": fit.lambda_tb_inf,
                "lambda_rel_error_vs_bessel_if_n2": rel_error,
                "delta_if_available": "" if fit.delta is None else fit.delta,
                "p_TB_if_available": "" if fit.p_tb is None else fit.p_tb,
                "c1_if_available": "" if fit.c1 is None else fit.c1,
                "c2_if_available": "" if fit.c2 is None else fit.c2,
                "RMSE": fit.rmse,
                "R2": fit.r2,
                "AIC_or_BIC_if_available": fit.aic,
                "leave_one_size_out_stability": fit.loo_stability,
                "model_notes": fit.notes,
            }
        )
    return rows


def summarize_gate(rows: Sequence[dict[str, object]], fits: Sequence[FitResult], baseline_metadata: dict[str, object]) -> dict[str, object]:
    """Classify the TB self-scaling gate."""
    n2_fits = [fit for fit in fits if np.isclose(fit.n, 2.0)]
    n2_errors = {
        fit.model: abs(float(fit.lambda_tb_inf) - N2_BESSEL_GROUND) / N2_BESSEL_GROUND
        for fit in n2_fits
    }
    n2_best_error = min(n2_errors.values())
    n2_lambda_spread = max(fit.lambda_tb_inf for fit in n2_fits) - min(fit.lambda_tb_inf for fit in n2_fits)
    n2_spread_rel = n2_lambda_spread / N2_BESSEL_GROUND
    calibration_ok = bool(n2_best_error < 0.01 and n2_spread_rel < 0.05)

    effective_fits = [fit for fit in fits if fit.model == "effective_radius"]
    effective_radius_kills = bool(
        all(fit.r2 > 0.999 for fit in effective_fits)
        and max(fit.rmse for fit in effective_fits) < 0.002
        and baseline_metadata["boundary_fraction_max_abs_mean_by_n"] < 0.001
    )
    boundary_kills = bool(
        baseline_metadata["boundary_fraction_r2"] > BOUNDARY_BASELINE_R2_GATE
        and baseline_metadata["boundary_fraction_loo_r2"] > 0.5
        and baseline_metadata["boundary_fraction_max_abs_mean_by_n"] < 0.001
    )
    pixelation_kills = bool(
        baseline_metadata["best_baseline_name"] != "boundary_fraction"
        and baseline_metadata["best_baseline_r2"] > BOUNDARY_BASELINE_R2_GATE
        and baseline_metadata["best_baseline_loo_r2"] > 0.5
        and baseline_metadata["best_baseline_max_abs_mean_by_n"] < 0.001
    )

    power_fits = [fit for fit in fits if fit.model == "power_law_residual"]
    p_values = {fit.n: fit.p_tb for fit in power_fits}
    p_stable = all("stable=True" in fit.loo_stability for fit in power_fits)
    lambda_by_n = {fit.n: fit.lambda_tb_inf for fit in effective_fits}

    if not calibration_ok:
        verdict = "TB_SELF_SCALING_INCONCLUSIVE"
    elif effective_radius_kills:
        verdict = "TB_SELF_SCALING_KILLED_EFFECTIVE_RADIUS_BASELINE"
    elif boundary_kills:
        verdict = "TB_SELF_SCALING_KILLED_BOUNDARY_FRACTION_BASELINE"
    elif pixelation_kills:
        verdict = "TB_SELF_SCALING_KILLED_PIXELATION_BASELINE"
    elif not p_stable:
        verdict = "TB_SELF_SCALING_INCONCLUSIVE"
    else:
        verdict = "TB_SELF_SCALING_INCONCLUSIVE"

    return {
        "verdict": verdict,
        "n2_errors": n2_errors,
        "n2_best_error": n2_best_error,
        "n2_lambda_spread_relative": n2_spread_rel,
        "calibration_ok": calibration_ok,
        "effective_radius_kills": effective_radius_kills,
        "boundary_fraction_kills": boundary_kills,
        "pixelation_kills": pixelation_kills,
        "p_values": p_values,
        "p_stable": p_stable,
        "lambda_by_n_effective_radius": lambda_by_n,
        "delta_by_n": {fit.n: fit.delta for fit in effective_fits},
        **baseline_metadata,
    }

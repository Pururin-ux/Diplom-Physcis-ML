"""Bessel-anchor sprint for Path B TB-to-continuum scaling.

This module is intentionally narrow: it computes only the circular
``n=2.0, rAR=1.0`` tight-binding anchor and compares it to exact Dirichlet disk
eigenvalues from Bessel zeros. It does not run shape comparisons, ML, Q, or S.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Iterable, Sequence

import numpy as np
from scipy.sparse.linalg import ArpackNoConvergence, eigsh
from scipy.special import jn_zeros

from .geometry import build_superellipse_dot
from .kwant_solver import _as_sorted_real_finite


ANCHOR_N = 2.0
ANCHOR_ASPECT_RATIO = 1.0
ANCHOR_SIZES = (24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0)
N_LEVELS = 6
FIT_STABILITY_P_RANGE_MAX = 1.0
RESIDUAL_DECREASE_RATIO_MAX = 0.8


@dataclass(frozen=True)
class BesselLevel:
    """Continuum disk eigenvalue metadata, including degeneracy labels."""

    level_index: int
    m: int
    s: int
    lambda_value: float
    degeneracy_group: str


@dataclass(frozen=True)
class PowerFit:
    """Power-law fit diagnostics for one level or degeneracy group."""

    level_or_group: str
    fit_model: str
    exponent_p: float
    coefficient_c: float
    intercept_if_used: float
    r2: float
    rmse: float
    leave_one_size_out_p_min: float
    leave_one_size_out_p_max: float
    leave_one_size_out_stable_true_false: bool
    verdict_for_level: str


def first_bessel_disk_levels(n_levels: int = N_LEVELS) -> list[BesselLevel]:
    """Return the first disk Dirichlet eigenvalues, including degeneracies."""
    candidates: list[tuple[float, int, int, int]] = []
    max_m = 8
    max_s = 8
    for m_value in range(max_m + 1):
        zeros = jn_zeros(m_value, max_s)
        degeneracy = 1 if m_value == 0 else 2
        for s_index, zero in enumerate(zeros, start=1):
            candidates.append((float(zero * zero), m_value, s_index, degeneracy))
    candidates.sort(key=lambda item: item[0])

    levels: list[BesselLevel] = []
    for lambda_value, m_value, s_index, degeneracy in candidates:
        group = f"m{m_value}_s{s_index}"
        for _ in range(degeneracy):
            levels.append(
                BesselLevel(
                    level_index=len(levels),
                    m=m_value,
                    s=s_index,
                    lambda_value=lambda_value,
                    degeneracy_group=group,
                )
            )
            if len(levels) == n_levels:
                return levels
    raise RuntimeError(f"Could not generate {n_levels} Bessel disk levels.")


def low_tb_levels_for_circle(a_value: float, n_levels: int = N_LEVELS) -> tuple[np.ndarray, int]:
    """Compute the lowest TB eigenvalues for the circular superellipse anchor."""
    fsys = build_superellipse_dot(a=float(a_value), b=float(a_value), n=ANCHOR_N)
    n_sites = len(fsys.sites)
    hamiltonian = fsys.hamiltonian_submatrix(sparse=True).tocsr()
    if n_sites <= n_levels + 1:
        values = np.linalg.eigvalsh(hamiltonian.toarray())
    else:
        solve_k = min(n_sites - 1, max(2 * n_levels, 12))
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
    return sorted_values[:n_levels], n_sites


def spectra_rows(sizes: Sequence[float] = ANCHOR_SIZES) -> list[dict[str, object]]:
    """Compute Bessel-anchor spectrum rows for all requested sizes."""
    bessel = first_bessel_disk_levels(N_LEVELS)
    rows: list[dict[str, object]] = []
    for a_value in sizes:
        tb_levels, _ = low_tb_levels_for_circle(float(a_value), N_LEVELS)
        for level in bessel:
            e_tb = float(tb_levels[level.level_index])
            e_kin = e_tb + 4.0
            lambda_over_a2 = level.lambda_value / (float(a_value) ** 2)
            residual = e_kin - lambda_over_a2
            rows.append(
                {
                    "a": float(a_value),
                    "level_index": level.level_index,
                    "E_TB": e_tb,
                    "E_kin_TB": e_kin,
                    "lambda_bessel": level.lambda_value,
                    "lambda_bessel_over_a2": lambda_over_a2,
                    "residual": residual,
                    "scaled_Ekin": (float(a_value) ** 2) * e_kin,
                    "scaled_residual": (float(a_value) ** 2) * residual,
                    "degeneracy_group": level.degeneracy_group,
                }
            )
    return rows


def _linear_fit(xs: np.ndarray, ys: np.ndarray) -> tuple[float, float, float, float]:
    """Return slope, intercept, R2, and RMSE for a simple linear fit."""
    design = np.column_stack([xs, np.ones_like(xs)])
    slope, intercept = np.linalg.lstsq(design, ys, rcond=None)[0]
    predicted = slope * xs + intercept
    residual = ys - predicted
    rmse = float(sqrt(float(np.mean(residual * residual))))
    ss_res = float(np.sum(residual * residual))
    ss_tot = float(np.sum((ys - float(np.mean(ys))) ** 2))
    r2 = 1.0 if ss_tot == 0.0 and ss_res == 0.0 else 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")
    return float(slope), float(intercept), r2, rmse


def _fit_power_law(a_values: np.ndarray, residuals: np.ndarray, signed: bool) -> tuple[float, float, float, float, float]:
    """Fit ``|R| ~ c*a^-p`` or same-sign signed residuals."""
    if signed:
        if np.any(residuals == 0.0) or not (np.all(residuals > 0.0) or np.all(residuals < 0.0)):
            return (float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))
        sign = 1.0 if np.all(residuals > 0.0) else -1.0
        y_values = np.abs(residuals)
    else:
        if np.any(residuals == 0.0):
            return (float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))
        sign = 1.0
        y_values = np.abs(residuals)

    slope, intercept, r2, rmse_log = _linear_fit(np.log(a_values), np.log(y_values))
    exponent = -slope
    coefficient = sign * exp(intercept)
    predicted = coefficient * np.power(a_values, -exponent)
    if not signed:
        predicted = np.abs(predicted)
        target = np.abs(residuals)
    else:
        target = residuals
    rmse = float(sqrt(float(np.mean((target - predicted) ** 2))))
    del rmse_log
    return float(exponent), float(coefficient), float(intercept), float(r2), rmse


def _leave_one_size_out_exponents(a_values: np.ndarray, residuals: np.ndarray, signed: bool) -> list[float]:
    """Return fitted exponents after leaving out each size."""
    exponents: list[float] = []
    for leave_out in range(len(a_values)):
        mask = np.ones(len(a_values), dtype=bool)
        mask[leave_out] = False
        exponent, *_ = _fit_power_law(a_values[mask], residuals[mask], signed=signed)
        if np.isfinite(exponent):
            exponents.append(float(exponent))
    return exponents


def _residual_magnitude_decreases(residuals: np.ndarray) -> bool:
    """Return whether final residual magnitude is materially smaller than first."""
    abs_values = np.abs(np.asarray(residuals, dtype=float))
    return bool(abs_values[-1] < RESIDUAL_DECREASE_RATIO_MAX * abs_values[0])


def _fit_verdict(exponent: float, p_min: float, p_max: float, residuals: np.ndarray) -> tuple[bool, str]:
    """Classify one level/group fit."""
    stable = bool(np.isfinite(exponent) and np.isfinite(p_min) and np.isfinite(p_max) and (p_max - p_min) <= FIT_STABILITY_P_RANGE_MAX)
    decreases = _residual_magnitude_decreases(residuals)
    if stable and decreases and exponent > 0.0:
        return True, "passed"
    if decreases and exponent > 0.0:
        return False, "inconclusive_unstable_exponent"
    if stable:
        return False, "inconclusive_residual_not_decreasing"
    return False, "failed_unstable"


def _rows_for_level(rows: Sequence[dict[str, object]], level_index: int) -> tuple[np.ndarray, np.ndarray]:
    """Return size and residual arrays for one individual level."""
    selected = [row for row in rows if int(row["level_index"]) == int(level_index)]
    selected.sort(key=lambda row: float(row["a"]))
    return (
        np.array([float(row["a"]) for row in selected], dtype=float),
        np.array([float(row["residual"]) for row in selected], dtype=float),
    )


def group_average_series(rows: Sequence[dict[str, object]], group: str) -> tuple[np.ndarray, np.ndarray]:
    """Return group-averaged residuals over degenerate continuum levels."""
    sizes = sorted({float(row["a"]) for row in rows})
    residuals: list[float] = []
    for a_value in sizes:
        values = [
            float(row["residual"])
            for row in rows
            if float(row["a"]) == a_value and str(row["degeneracy_group"]) == group
        ]
        residuals.append(float(np.mean(values)))
    return np.array(sizes, dtype=float), np.array(residuals, dtype=float)


def fit_rows(rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    """Build power-law fit rows for individual levels and degeneracy groups."""
    out: list[dict[str, object]] = []
    targets: list[tuple[str, np.ndarray, np.ndarray]] = []
    for level_index in sorted({int(row["level_index"]) for row in rows}):
        a_values, residuals = _rows_for_level(rows, level_index)
        targets.append((f"level_{level_index}", a_values, residuals))
    for group in sorted({str(row["degeneracy_group"]) for row in rows}):
        a_values, residuals = group_average_series(rows, group)
        targets.append((f"group_{group}", a_values, residuals))

    for target_name, a_values, residuals in targets:
        for model_name, signed in (("abs_power_law", False), ("signed_power_law", True)):
            exponent, coefficient, intercept, r2, rmse = _fit_power_law(a_values, residuals, signed=signed)
            loo = _leave_one_size_out_exponents(a_values, residuals, signed=signed)
            p_min = float(np.min(loo)) if loo else float("nan")
            p_max = float(np.max(loo)) if loo else float("nan")
            stable, verdict = _fit_verdict(exponent, p_min, p_max, residuals)
            out.append(
                {
                    "level_or_group": target_name,
                    "fit_model": model_name,
                    "exponent_p": exponent,
                    "coefficient_c": coefficient,
                    "intercept_if_used": intercept,
                    "R2": r2,
                    "RMSE": rmse,
                    "leave_one_size_out_p_min": p_min,
                    "leave_one_size_out_p_max": p_max,
                    "leave_one_size_out_stable_true_false": stable,
                    "verdict_for_level": verdict,
                }
            )
    return out


def numerical_checks(rows: Sequence[dict[str, object]]) -> dict[str, bool]:
    """Return Bessel-anchor numerical and monotonic sanity checks."""
    levels_by_size: dict[float, list[float]] = {}
    ekin_by_level: dict[int, list[float]] = {}
    scaled_error_by_level: dict[int, list[float]] = {}
    for row in rows:
        levels_by_size.setdefault(float(row["a"]), []).append(float(row["E_TB"]))
        ekin_by_level.setdefault(int(row["level_index"]), []).append(float(row["E_kin_TB"]))
        scaled_error_by_level.setdefault(int(row["level_index"]), []).append(
            abs(float(row["scaled_Ekin"]) - float(row["lambda_bessel"]))
        )

    finite_sorted = True
    for values in levels_by_size.values():
        arr = np.array(values, dtype=float)
        finite_sorted = finite_sorted and bool(np.all(np.isfinite(arr)) and np.all(np.diff(arr) >= -1e-12))

    positive_ekin = all(float(row["E_kin_TB"]) > 0.0 and np.isfinite(float(row["E_kin_TB"])) for row in rows)
    ekin_decreases = True
    scaled_approaches = True
    for level_index in sorted(ekin_by_level):
        ekin_values = np.array(ekin_by_level[level_index], dtype=float)
        scaled_errors = np.array(scaled_error_by_level[level_index], dtype=float)
        ekin_decreases = ekin_decreases and bool(np.all(np.diff(ekin_values) < 0.0))
        scaled_approaches = scaled_approaches and bool(scaled_errors[-1] < scaled_errors[0])
    return {
        "spectra_finite_sorted": finite_sorted,
        "ekin_positive": positive_ekin,
        "ekin_decreases_with_a": ekin_decreases,
        "scaled_values_approach_bessel": scaled_approaches,
    }


def degeneracy_summary(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    """Summarize whether continuum degeneracies are explicitly represented."""
    groups = sorted({str(row["degeneracy_group"]) for row in rows})
    group_sizes = {
        group: len({int(row["level_index"]) for row in rows if str(row["degeneracy_group"]) == group})
        for group in groups
    }
    split_by_group: dict[str, float] = {}
    for group, count in group_sizes.items():
        if count < 2:
            continue
        max_split = 0.0
        for a_value in sorted({float(row["a"]) for row in rows}):
            values = [
                float(row["E_kin_TB"])
                for row in rows
                if str(row["degeneracy_group"]) == group and float(row["a"]) == a_value
            ]
            max_split = max(max_split, max(values) - min(values))
        split_by_group[group] = float(max_split)
    return {
        "groups": groups,
        "group_sizes": group_sizes,
        "max_tb_splitting_by_degenerate_group": split_by_group,
        "degeneracy_reported": bool(any(count > 1 for count in group_sizes.values())),
    }


def final_verdict(rows: Sequence[dict[str, object]], fits: Sequence[dict[str, object]]) -> tuple[str, list[str]]:
    """Return the final Bessel-anchor verdict and reasons."""
    checks = numerical_checks(rows)
    reasons: list[str] = []
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        return "BESSEL_ANCHOR_FAILED", [f"Numerical sanity checks failed: {', '.join(failed)}."]

    degeneracy = degeneracy_summary(rows)
    if not bool(degeneracy["degeneracy_reported"]):
        return "BESSEL_ANCHOR_FAILED", ["Continuum degeneracy handling was not reported."]

    abs_fits = {
        str(row["level_or_group"]): row for row in fits if str(row["fit_model"]) == "abs_power_law"
    }
    required_targets = ("level_0", "level_1", "level_2", "group_m0_s1", "group_m1_s1")
    missing = [target for target in required_targets if target not in abs_fits]
    if missing:
        return "BESSEL_ANCHOR_FAILED", [f"Missing required fit targets: {', '.join(missing)}."]

    passed_targets = [
        target for target in required_targets if str(abs_fits[target]["verdict_for_level"]) == "passed"
    ]
    inconclusive_targets = [
        target for target in required_targets if "inconclusive" in str(abs_fits[target]["verdict_for_level"])
    ]
    failed_targets = [
        target
        for target in required_targets
        if str(abs_fits[target]["verdict_for_level"]).startswith("failed")
    ]

    if len(passed_targets) == len(required_targets):
        return "BESSEL_ANCHOR_PASSED", ["Ground and main low-level residual fits were stable and decreasing."]
    if failed_targets:
        return "BESSEL_ANCHOR_FAILED", [f"Unstable required targets: {', '.join(failed_targets)}."]

    reasons.append(f"Passed targets: {', '.join(passed_targets) if passed_targets else 'none'}.")
    reasons.append(f"Inconclusive targets: {', '.join(inconclusive_targets) if inconclusive_targets else 'none'}.")
    return "BESSEL_ANCHOR_INCONCLUSIVE", reasons


def run_bessel_anchor() -> dict[str, object]:
    """Run the complete Bessel-anchor computation in memory."""
    rows = spectra_rows(ANCHOR_SIZES)
    fits = fit_rows(rows)
    verdict, reasons = final_verdict(rows, fits)
    return {
        "spectra_rows": rows,
        "fit_rows": fits,
        "numerical_checks": numerical_checks(rows),
        "degeneracy_summary": degeneracy_summary(rows),
        "verdict": verdict,
        "verdict_reasons": reasons,
    }

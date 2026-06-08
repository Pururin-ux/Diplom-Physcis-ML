"""Open-transport contact-coupling preflight for superellipse dots.

This module builds two-terminal Kwant systems and tests whether contact width
or lead mode thresholds dominate conductance before any larger shape scan. It
does not use finite-difference references, closed-spectrum residuals, ML, or
Q/S objectives.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import cos, pi, sqrt
from typing import Sequence

import kwant
import numpy as np


A_VALUE = 30.0
ASPECT_RATIO = 1.0
N_VALUES = (1.2, 2.0, 4.0)
PRIMARY_LEAD_WIDTHS = (4, 10)
ENERGY_MIN = -3.8
ENERGY_MAX = -3.0
N_ENERGIES = 241
CONTACT_DOMINANCE_TOLERANCE = 0.95


@dataclass(frozen=True)
class CurveMetrics:
    """Compact descriptors of one conductance curve."""

    mean: float
    variance: float
    integrated: float
    total_variation: float
    maxima_indices: tuple[int, ...]
    minima_indices: tuple[int, ...]


def centered_lead_y_values(width: int) -> tuple[int, ...]:
    """Return integer transverse coordinates for a centered strip lead."""
    if int(width) <= 0:
        raise ValueError("lead width must be positive.")
    start = -int(width) // 2
    return tuple(range(start, start + int(width)))


def _inside_superellipse(x_value: int, y_value: int, a_value: float, aspect_ratio: float, n_value: float) -> bool:
    """Return whether an integer site is inside the superellipse."""
    b_value = float(a_value) * float(aspect_ratio)
    return abs(float(x_value) / float(a_value)) ** float(n_value) + abs(float(y_value) / b_value) ** float(n_value) <= 1.0


def _dot_or_contact_site(pos: tuple[float, float], a_value: float, aspect_ratio: float, n_value: float, lead_width: int) -> bool:
    """Return whether a site belongs to the dot plus flat contact slices."""
    x_raw, y_raw = pos
    x_value = int(x_raw)
    y_value = int(y_raw)
    radius = int(round(float(a_value)))
    if _inside_superellipse(x_value, y_value, float(a_value), float(aspect_ratio), float(n_value)):
        return True
    # One lattice-column contact slice on each side. This makes the strip-lead
    # interface explicit and reproducible without adding a long channel.
    return abs(x_value) == radius and y_value in centered_lead_y_values(int(lead_width))


def build_open_transport_system(
    n_value: float,
    lead_width: int,
    a_value: float = A_VALUE,
    aspect_ratio: float = ASPECT_RATIO,
) -> kwant.system.FiniteSystem:
    """Build a finalized two-terminal open superellipse transport system."""
    if float(a_value) <= 0 or float(aspect_ratio) <= 0 or float(n_value) <= 0:
        raise ValueError("a_value, aspect_ratio, and n_value must be positive.")
    radius = int(round(float(a_value)))
    lat = kwant.lattice.square(a=1, norbs=1)
    system = kwant.Builder()

    def scattering_shape(pos: tuple[float, float]) -> bool:
        return _dot_or_contact_site(pos, float(a_value), float(aspect_ratio), float(n_value), int(lead_width))

    system[lat.shape(scattering_shape, (0, 0))] = 0.0
    system[lat.neighbors()] = -1.0

    y_values = centered_lead_y_values(int(lead_width))

    left_lead = kwant.Builder(kwant.TranslationalSymmetry((-1, 0)))
    for y_value in y_values:
        left_lead[lat(-radius - 1, y_value)] = 0.0
    left_lead[lat.neighbors()] = -1.0

    right_lead = kwant.Builder(kwant.TranslationalSymmetry((1, 0)))
    for y_value in y_values:
        right_lead[lat(radius + 1, y_value)] = 0.0
    right_lead[lat.neighbors()] = -1.0

    system.attach_lead(left_lead)
    system.attach_lead(right_lead)
    return system.finalized()


def build_straight_channel_system(
    lead_width: int,
    a_value: float = A_VALUE,
) -> kwant.system.FiniteSystem:
    """Build a straight strip channel with the same lead width and length."""
    radius = int(round(float(a_value)))
    lat = kwant.lattice.square(a=1, norbs=1)
    y_values = set(centered_lead_y_values(int(lead_width)))
    system = kwant.Builder()
    for x_value in range(-radius, radius + 1):
        for y_value in y_values:
            system[lat(x_value, y_value)] = 0.0
    system[lat.neighbors()] = -1.0

    left_lead = kwant.Builder(kwant.TranslationalSymmetry((-1, 0)))
    for y_value in y_values:
        left_lead[lat(-radius - 1, y_value)] = 0.0
    left_lead[lat.neighbors()] = -1.0

    right_lead = kwant.Builder(kwant.TranslationalSymmetry((1, 0)))
    for y_value in y_values:
        right_lead[lat(radius + 1, y_value)] = 0.0
    right_lead[lat.neighbors()] = -1.0

    system.attach_lead(left_lead)
    system.attach_lead(right_lead)
    return system.finalized()


def lead_mode_count(energy: float, lead_width: int) -> int:
    """Estimate propagating modes for a square-lattice strip lead."""
    count = 0
    for mode_index in range(1, int(lead_width) + 1):
        transverse = -2.0 * cos(pi * mode_index / (int(lead_width) + 1))
        cosine_k = -(float(energy) - transverse) / 2.0
        if abs(cosine_k) <= 1.0:
            count += 1
    return count


def lead_mode_thresholds(lead_width: int, energy_min: float = ENERGY_MIN, energy_max: float = ENERGY_MAX) -> list[float]:
    """Return strip-lead subband threshold energies inside the scan window."""
    thresholds: list[float] = []
    for mode_index in range(1, int(lead_width) + 1):
        transverse = -2.0 * cos(pi * mode_index / (int(lead_width) + 1))
        for threshold in (transverse - 2.0, transverse + 2.0):
            if float(energy_min) <= threshold <= float(energy_max):
                thresholds.append(float(threshold))
    return sorted(thresholds)


def conductance_curve(
    system: kwant.system.FiniteSystem,
    energies: Sequence[float],
    lead_width: int,
) -> tuple[list[dict[str, object]], int]:
    """Compute spinless two-terminal conductance over an energy grid."""
    rows: list[dict[str, object]] = []
    failures = 0
    for energy in energies:
        try:
            smatrix = kwant.smatrix(system, float(energy))
            transmission = float(smatrix.transmission(1, 0))
        except Exception as exc:  # Kwant can raise several solver-specific errors near thresholds.
            transmission = float("nan")
            failures += 1
            note = type(exc).__name__
        else:
            note = ""
        rows.append(
            {
                "energy": float(energy),
                "transmission": transmission,
                "conductance_spinless_units": transmission,
                "lead_mode_count_if_available": lead_mode_count(float(energy), int(lead_width)),
                "notes": note,
            }
        )
    return rows, failures


def extract_curve_metrics(energies: Sequence[float], conductance: Sequence[float]) -> CurveMetrics:
    """Extract mean, variation, and simple extrema from a conductance curve."""
    e_values = np.asarray(energies, dtype=float)
    g_values = np.asarray(conductance, dtype=float)
    finite = np.isfinite(g_values)
    if finite.sum() < 3:
        return CurveMetrics(float("nan"), float("nan"), float("nan"), float("nan"), tuple(), tuple())
    g_clean = g_values[finite]
    e_clean = e_values[finite]
    maxima: list[int] = []
    minima: list[int] = []
    threshold = max(0.02 * float(np.nanmax(g_clean) - np.nanmin(g_clean)), 1e-6)
    for index in range(1, len(g_values) - 1):
        if not np.isfinite(g_values[index - 1 : index + 2]).all():
            continue
        if g_values[index] > g_values[index - 1] + threshold and g_values[index] > g_values[index + 1] + threshold:
            maxima.append(index)
        if g_values[index] < g_values[index - 1] - threshold and g_values[index] < g_values[index + 1] - threshold:
            minima.append(index)
    return CurveMetrics(
        mean=float(np.mean(g_clean)),
        variance=float(np.var(g_clean)),
        integrated=float(np.trapezoid(g_clean, e_clean)),
        total_variation=float(np.sum(np.abs(np.diff(g_clean)))),
        maxima_indices=tuple(maxima),
        minima_indices=tuple(minima),
    )


def normalized_curve_distance(curve_a: Sequence[float], curve_b: Sequence[float]) -> float:
    """Return RMS curve distance normalized by combined RMS scale."""
    a_arr = np.asarray(curve_a, dtype=float)
    b_arr = np.asarray(curve_b, dtype=float)
    finite = np.isfinite(a_arr) & np.isfinite(b_arr)
    if finite.sum() == 0:
        return float("inf")
    diff = a_arr[finite] - b_arr[finite]
    numerator = sqrt(float(np.mean(diff * diff)))
    denominator = sqrt(float(np.mean(a_arr[finite] ** 2) + np.mean(b_arr[finite] ** 2)))
    return numerator / denominator if denominator > 0.0 else numerator


def shift_rescale_distance(curve_a: Sequence[float], curve_b: Sequence[float], max_shift: int = 12) -> float:
    """Return best normalized distance after index shift and affine rescaling."""
    a_arr = np.asarray(curve_a, dtype=float)
    b_arr = np.asarray(curve_b, dtype=float)
    best = float("inf")
    for shift in range(-int(max_shift), int(max_shift) + 1):
        if shift < 0:
            a_slice = a_arr[-shift:]
            b_slice = b_arr[: len(a_slice)]
        elif shift > 0:
            a_slice = a_arr[:-shift]
            b_slice = b_arr[shift:]
        else:
            a_slice = a_arr
            b_slice = b_arr
        finite = np.isfinite(a_slice) & np.isfinite(b_slice)
        if finite.sum() < 3:
            continue
        design = np.column_stack([a_slice[finite], np.ones(finite.sum())])
        alpha, beta = np.linalg.lstsq(design, b_slice[finite], rcond=None)[0]
        adjusted = alpha * a_slice + beta
        best = min(best, normalized_curve_distance(adjusted, b_slice))
    return best


def typical_shape_effect(curves: dict[float, np.ndarray]) -> float:
    """Return mean pairwise distance among n curves for one lead width."""
    distances = [
        normalized_curve_distance(curves[left], curves[right])
        for left, right in combinations(sorted(curves), 2)
    ]
    return float(np.mean(distances)) if distances else float("inf")


def feature_energies(metrics: CurveMetrics, energies: Sequence[float]) -> tuple[list[float], list[float]]:
    """Return extrema energies from curve metrics."""
    energy_arr = np.asarray(energies, dtype=float)
    maxima = [float(energy_arr[index]) for index in metrics.maxima_indices]
    minima = [float(energy_arr[index]) for index in metrics.minima_indices]
    return maxima, minima


def features_align_with_mode_thresholds(feature_values: Sequence[float], thresholds: Sequence[float], tolerance: float) -> bool:
    """Return whether most feature energies are near lead mode thresholds."""
    values = [float(value) for value in feature_values if np.isfinite(float(value))]
    if not values or not thresholds:
        return False
    hits = sum(any(abs(value - threshold) <= float(tolerance) for threshold in thresholds) for value in values)
    return hits / len(values) >= 0.5


def classify_preflight(
    contact_effect_size: float,
    shape_effect_size_w4: float,
    shape_effect_size_w10: float,
    mode_threshold_kills: bool,
    straight_channel_kills: bool,
    energy_shift_kills: bool,
    numerical_instability: bool,
) -> str:
    """Return the final open-transport preflight verdict."""
    if numerical_instability:
        return "OPEN_TRANSPORT_PREFLIGHT_INCONCLUSIVE"
    if mode_threshold_kills:
        return "OPEN_TRANSPORT_PREFLIGHT_KILLED_MODE_THRESHOLDS"
    contact_dominates = (
        contact_effect_size >= CONTACT_DOMINANCE_TOLERANCE * shape_effect_size_w4
        and contact_effect_size >= CONTACT_DOMINANCE_TOLERANCE * shape_effect_size_w10
    )
    if contact_dominates:
        return "OPEN_TRANSPORT_PREFLIGHT_KILLED_CONTACT_DOMINANCE"
    if straight_channel_kills:
        return "OPEN_TRANSPORT_PREFLIGHT_KILLED_STRAIGHT_CHANNEL"
    if energy_shift_kills:
        return "OPEN_TRANSPORT_PREFLIGHT_KILLED_ENERGY_SHIFT_ONLY"
    return "OPEN_TRANSPORT_PREFLIGHT_CONTACT_STABLE_PROMISING"

"""Tests for the open-transport contact preflight helpers."""

from __future__ import annotations

import numpy as np
import kwant

from src.open_transport_preflight import (
    build_open_transport_system,
    centered_lead_y_values,
    extract_curve_metrics,
    lead_mode_count,
    normalized_curve_distance,
    shift_rescale_distance,
)


def test_centered_lead_y_values_has_requested_width() -> None:
    """The lead strip coordinate helper should preserve width."""
    assert centered_lead_y_values(4) == (-2, -1, 0, 1)
    assert len(centered_lead_y_values(10)) == 10


def test_transport_system_builder_has_two_leads() -> None:
    """A small open dot should finalize with two attached leads."""
    system = build_open_transport_system(n_value=2.0, lead_width=4, a_value=8.0)

    assert len(system.sites) > 0
    assert len(system.leads) == 2


def test_smatrix_computes_at_safe_energy() -> None:
    """The contact convention should support a finite smatrix calculation."""
    system = build_open_transport_system(n_value=2.0, lead_width=4, a_value=8.0)
    smatrix = kwant.smatrix(system, -3.2)

    assert np.isfinite(float(smatrix.transmission(1, 0)))


def test_feature_extraction_detects_synthetic_extrema() -> None:
    """Synthetic peaks and dips should be detected by feature extraction."""
    energies = np.linspace(-1.0, 1.0, 7)
    conductance = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0])

    metrics = extract_curve_metrics(energies, conductance)

    assert len(metrics.maxima_indices) == 2
    assert len(metrics.minima_indices) == 1


def test_curve_distance_identical_and_shift_rescale() -> None:
    """Distance should vanish for identical and affine-rescaled curves."""
    curve = np.array([0.0, 1.0, 2.0, 1.0])
    affine = 3.0 * curve + 2.0

    assert normalized_curve_distance(curve, curve) == 0.0
    assert shift_rescale_distance(curve, affine, max_shift=0) < 1e-12


def test_lead_mode_count_increases_after_threshold() -> None:
    """The strip-mode estimate should reflect a threshold opening."""
    assert lead_mode_count(-3.8, 4) == 0
    assert lead_mode_count(-3.2, 4) >= 1

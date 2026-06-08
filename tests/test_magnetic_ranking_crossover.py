"""Tests for the exploratory magnetic ranking-crossover sprint."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src.magnetic_ranking_crossover import (
    ALPHA0_REPRODUCTION_TOL,
    EIGEN_IMAG_TOL,
    GAUGE_INVARIANCE_TOL,
    GAUGE_LANDAU,
    GAUGE_SYMMETRIC,
    HERMITICITY_TOL,
    SHAPES,
    WEAK_ALPHAS,
    compute_spectrum_row,
    magnetic_length,
    symmetry_artifact_rows,
    zero_field_reference_spectrum,
)


def _levels(row: dict[str, object]) -> np.ndarray:
    return np.array([float(row[f"E{i}"]) for i in range(6)], dtype=float)


def test_alpha0_magnetic_builder_reproduces_zero_field_spectrum() -> None:
    """At alpha=0, the magnetic builder should match the existing builder."""
    shape = SHAPES[0]
    computed = compute_spectrum_row(shape, a=8.0, alpha=0.0, gauge=GAUGE_LANDAU)
    reference = zero_field_reference_spectrum(a=8.0, b=8.0, n=2.0, k=6)

    assert np.max(np.abs(_levels(computed.row) - reference)) < ALPHA0_REPRODUCTION_TOL


def test_magnetic_hamiltonian_is_hermitian_for_nonzero_alpha() -> None:
    """The Peierls-phase Hamiltonian must remain Hermitian."""
    computed = compute_spectrum_row(SHAPES[2], a=8.0, alpha=0.005, gauge=GAUGE_LANDAU)

    assert computed.max_hermiticity_error < HERMITICITY_TOL


def test_magnetic_eigenvalues_are_real_sorted_and_finite() -> None:
    """Low-energy eigenvalues should be real-valued, finite, and sorted."""
    computed = compute_spectrum_row(SHAPES[3], a=8.0, alpha=0.005, gauge=GAUGE_LANDAU)
    levels = _levels(computed.row)

    assert computed.max_eigen_imag < EIGEN_IMAG_TOL
    assert np.all(np.isfinite(levels))
    assert np.all(np.diff(levels) >= -1e-12)


def test_spectrum_metadata_includes_field_and_flux_diagnostics() -> None:
    """Magnetic output rows must include the interpretation diagnostics."""
    computed = compute_spectrum_row(SHAPES[1], a=8.0, alpha=0.005, gauge=GAUGE_LANDAU)

    required = {
        "alpha",
        "gauge",
        "l_B",
        "l_B_over_a",
        "phi_total",
        "phi_total_area_proxy",
        "N_plaquettes_inside_dot",
        "geometry_hash",
    }
    assert required.issubset(computed.row)
    assert np.isclose(float(computed.row["l_B"]), magnetic_length(0.005))
    assert float(computed.row["phi_total"]) > 0.0


def test_landau_and_symmetric_gauge_match_for_required_circle_case() -> None:
    """Required gauge-control case: n=2, rAR=1, a=30, alpha=0.005."""
    shape = SHAPES[0]
    landau = compute_spectrum_row(shape, a=30.0, alpha=0.005, gauge=GAUGE_LANDAU)
    symmetric = compute_spectrum_row(shape, a=30.0, alpha=0.005, gauge=GAUGE_SYMMETRIC)

    assert np.max(np.abs(_levels(landau.row) - _levels(symmetric.row))) < GAUGE_INVARIANCE_TOL


def test_circle_symmetry_artifact_diagnostic_reports_split_12() -> None:
    """Circle rows should report E2-E1 splitting for every alpha."""
    rows = [compute_spectrum_row(SHAPES[0], a=8.0, alpha=alpha, gauge=GAUGE_LANDAU).row for alpha in WEAK_ALPHAS]
    diagnostics = symmetry_artifact_rows(rows)

    assert len(diagnostics) == len(WEAK_ALPHAS)
    assert all("split_12" in row for row in diagnostics)
    assert all(float(row["split_12"]) >= -1e-12 for row in diagnostics)

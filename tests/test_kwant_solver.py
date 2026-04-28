"""Minimal sanity tests for rectangular-dot geometry and spectrum solver."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src.geometry import build_rectangular_dot
from src.kwant_solver import _as_sorted_real_finite, lowest_four_energies


def test_as_sorted_real_finite_sorts_real_finite_values() -> None:
    """Validation helper should return finite real values in ascending order."""
    vals = np.array([2.0, -1.0, 0.5], dtype=float)

    out = _as_sorted_real_finite(vals)

    assert np.array_equal(out, np.array([-1.0, 0.5, 2.0], dtype=float))


def test_as_sorted_real_finite_rejects_complex_values() -> None:
    """Closed Hermitian spectra should not accept genuinely complex values."""
    vals = np.array([1.0 + 0.1j, 2.0 + 0.0j])

    with pytest.raises(ValueError, match="Eigenvalues must be real"):
        _as_sorted_real_finite(vals)


def test_as_sorted_real_finite_rejects_non_finite_values() -> None:
    """NaN or infinite eigenvalues should fail validation."""
    vals = np.array([0.0, np.nan, np.inf], dtype=float)

    with pytest.raises(ValueError, match="non-finite"):
        _as_sorted_real_finite(vals)


def test_build_rectangular_dot_site_count_and_hamiltonian_shape() -> None:
    """Finalized dot should have Lx*Ly sites and matching Hamiltonian shape."""
    lx, ly = 6, 5
    fsys = build_rectangular_dot(lx, ly)
    h = fsys.hamiltonian_submatrix(sparse=True)
    n_sites = lx * ly
    assert len(fsys.sites) == n_sites
    assert h.shape == (n_sites, n_sites)


def test_lowest_four_energies_normal_case_properties() -> None:
    """Normal-size system should return four finite sorted energies."""
    energies = lowest_four_energies(6, 5)
    assert energies.shape == (4,)
    assert np.all(np.isfinite(energies))
    assert np.all(np.diff(energies) >= 0.0)


def test_lowest_four_energies_reproducible_for_same_input() -> None:
    """Repeated calls with same geometry should be reproducible."""
    e1 = lowest_four_energies(7, 6)
    e2 = lowest_four_energies(7, 6)
    assert np.allclose(e1, e2, rtol=0.0, atol=1e-12)


def test_square_case_degeneracy_is_not_treated_as_error() -> None:
    """Square geometries may have (near-)degenerate levels; this is acceptable."""
    energies = lowest_four_energies(8, 8)
    gaps = np.diff(energies)
    assert energies.shape == (4,)
    assert np.all(np.isfinite(energies))
    assert np.all(gaps >= 0.0)
    assert np.min(np.abs(gaps)) < 1e-6

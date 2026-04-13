"""Minimal sanity tests for rectangular-dot geometry and spectrum solver."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src.geometry import build_rectangular_dot
from src.kwant_solver import lowest_four_energies


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

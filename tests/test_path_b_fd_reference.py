"""Tests for the Path B finite-difference continuum reference."""

from __future__ import annotations

import numpy as np

from src.path_b_fd_reference import (
    build_dirichlet_laplacian,
    first_bessel_disk_levels,
    lowest_fd_eigenvalues,
    superellipse_mask,
)


def test_superellipse_mask_has_strict_interior_and_excludes_boundary() -> None:
    """The mask should include interior points but not boundary points."""
    mask, h = superellipse_mask(n_value=2.0, aspect_ratio=1.0, n_grid=21)
    center = 10

    assert h == 0.1
    assert mask[center, center]
    assert not mask[0, center]
    assert not mask[-1, center]


def test_dirichlet_laplacian_shape_and_symmetry() -> None:
    """The sparse FD Laplacian should be square and symmetric."""
    fd = build_dirichlet_laplacian(n_value=2.0, aspect_ratio=1.0, n_grid=31)

    assert fd.matrix.shape == (fd.num_interior_points, fd.num_interior_points)
    diff = fd.matrix - fd.matrix.T
    assert diff.nnz == 0 or np.max(np.abs(diff.data)) < 1e-12


def test_fd_eigenvalues_are_finite_positive_sorted_for_small_grid() -> None:
    """A small grid should produce finite positive sorted eigenvalues."""
    values, _ = lowest_fd_eigenvalues(n_value=1.2, aspect_ratio=1.0, n_grid=41, n_levels=4)

    assert values.shape == (4,)
    assert np.all(np.isfinite(values))
    assert np.all(values > 0.0)
    assert np.all(np.diff(values) >= 0.0)


def test_circle_ground_state_fd_close_to_bessel_at_moderate_grid() -> None:
    """Circle FD ground state should be reasonably close to j_01^2."""
    values, _ = lowest_fd_eigenvalues(n_value=2.0, aspect_ratio=1.0, n_grid=81, n_levels=1)
    bessel = first_bessel_disk_levels(1)[0].lambda_value
    rel_error = abs(float(values[0]) - bessel) / bessel

    assert rel_error < 0.05

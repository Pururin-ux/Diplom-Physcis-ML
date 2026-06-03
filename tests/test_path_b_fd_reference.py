"""Tests for the Path B finite-difference continuum reference."""

from __future__ import annotations

import numpy as np

from src.path_b_fd_reference import (
    build_dirichlet_laplacian,
    first_bessel_disk_levels,
    lowest_fd_eigenvalues,
    observed_order_from_three_values,
    reference_uncertainty,
    richardson_extrapolate,
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


def test_observed_order_solver_handles_unequal_grid_steps() -> None:
    """The p solver should recover synthetic unequal-step convergence."""
    h_values = [0.3, 0.17, 0.08]
    p_true = 1.75
    lambda_inf = 5.0
    coefficient = -2.3
    values = [lambda_inf + coefficient * h**p_true for h in h_values]

    p_estimate = observed_order_from_three_values(h_values, values)

    assert p_estimate is not None
    assert abs(p_estimate - p_true) < 1e-10


def test_observed_order_solver_returns_none_without_positive_ratio() -> None:
    """Non-convergent three-point data should not produce a fake p value."""
    p_estimate = observed_order_from_three_values([0.3, 0.2, 0.1], [1.0, 2.0, 1.5])

    assert p_estimate is None


def test_richardson_extrapolate_recovers_synthetic_limit() -> None:
    """Two-grid Richardson extrapolation should recover lambda_inf."""
    lambda_inf = 7.5
    coefficient = 1.2
    p_value = 2.4
    h_coarse = 0.2
    h_fine = 0.1
    lambda_coarse = lambda_inf + coefficient * h_coarse**p_value
    lambda_fine = lambda_inf + coefficient * h_fine**p_value

    extrapolated = richardson_extrapolate(lambda_coarse, lambda_fine, h_coarse, h_fine, p_value)

    assert abs(extrapolated - lambda_inf) < 1e-12


def test_reference_uncertainty_uses_candidate_spread() -> None:
    """Reference uncertainty should report absolute and relative spread."""
    uncertainty, relative = reference_uncertainty([9.9, 10.0, 10.1], 10.0)

    assert np.isclose(uncertainty, 0.2)
    assert np.isclose(relative, 0.02)

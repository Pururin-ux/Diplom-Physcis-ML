"""Tests for the Path B TB-only self-scaling gate."""

from __future__ import annotations

import numpy as np

from src.path_b_tb_self_scaling import (
    N2_BESSEL_GROUND,
    count_boundary_sites,
    effective_radius_y,
    fit_effective_radius,
)


def test_boundary_site_count_for_solid_square() -> None:
    """Every site in a 2x2 solid square is a boundary site."""
    coords = {(0, 0), (1, 0), (0, 1), (1, 1)}

    assert count_boundary_sites(coords) == 4


def test_boundary_site_count_has_interior_for_3x3_square() -> None:
    """A 3x3 solid square has eight boundary sites and one interior site."""
    coords = {(x_value, y_value) for x_value in range(3) for y_value in range(3)}

    assert count_boundary_sites(coords) == 8


def test_effective_radius_fit_recovers_synthetic_parameters() -> None:
    """The effective-radius fit should recover a noiseless synthetic model."""
    a_values = np.array([24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0])
    lambda_true = 8.2
    delta_true = 0.7
    y_values = effective_radius_y(a_values, lambda_true, delta_true)

    lambda_fit, delta_fit, prediction = fit_effective_radius(a_values, y_values)

    assert abs(lambda_fit - lambda_true) < 1e-10
    assert abs(delta_fit - delta_true) < 1e-10
    assert np.allclose(prediction, y_values)


def test_n2_bessel_ground_constant() -> None:
    """The disk ground reference should match j01^2."""
    assert abs(N2_BESSEL_GROUND - 5.783185962946785) < 1e-12

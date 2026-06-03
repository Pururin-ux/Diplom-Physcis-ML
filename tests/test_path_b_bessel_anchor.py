"""Unit tests for the Path B Bessel-anchor helpers."""

from __future__ import annotations

import numpy as np

from src.path_b_bessel_anchor import first_bessel_disk_levels, fit_rows


def test_first_bessel_disk_levels_include_expected_degeneracies() -> None:
    """The first six disk levels should include m>0 degeneracies."""
    levels = first_bessel_disk_levels(6)

    groups = [level.degeneracy_group for level in levels]
    assert groups == ["m0_s1", "m1_s1", "m1_s1", "m2_s1", "m2_s1", "m0_s2"]
    assert levels[1].lambda_value == levels[2].lambda_value
    assert levels[3].lambda_value == levels[4].lambda_value
    assert levels[0].lambda_value < levels[1].lambda_value < levels[3].lambda_value


def test_fit_rows_recovers_simple_power_law() -> None:
    """Power-law fitting should recover a synthetic residual exponent."""
    sizes = np.array([24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0])
    rows: list[dict[str, object]] = []
    for a_value in sizes:
        residual = 3.0 * a_value ** -2.0
        rows.append(
            {
                "a": a_value,
                "level_index": 0,
                "E_TB": -4.0 + residual,
                "E_kin_TB": residual,
                "lambda_bessel": 0.0,
                "lambda_bessel_over_a2": 0.0,
                "residual": residual,
                "scaled_Ekin": a_value * a_value * residual,
                "scaled_residual": a_value * a_value * residual,
                "degeneracy_group": "m0_s1",
            }
        )

    fits = fit_rows(rows)
    level_fit = next(row for row in fits if row["level_or_group"] == "level_0" and row["fit_model"] == "abs_power_law")

    assert np.isclose(float(level_fit["exponent_p"]), 2.0)
    assert bool(level_fit["leave_one_size_out_stable_true_false"])

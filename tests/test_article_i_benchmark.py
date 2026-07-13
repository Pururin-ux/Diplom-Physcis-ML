"""Tests for the Article-I continuum disk benchmark."""

from __future__ import annotations

import math

from src import article_i_benchmark as b


def test_bessel_ratio_value():
    assert abs(b.DISK_CHIH_SPLIT - 2.538734) < 1e-5


def test_slope_pair_is_symmetric_and_matches_gap():
    lo, hi = b.DISK_SLOPE_PAIR
    assert abs(lo + hi) < 1e-12                      # symmetric about zero
    assert abs((hi - lo) - b.DISK_CHIH_SPLIT) < 1e-12  # gap slope = split coeff


def test_gap_slope_scale_dependence():
    # gap slope scales as 1/a0^2; dimensionless split is scale-free
    assert abs(b.gap_slope(1.0) - b.J11 ** 2) < 1e-9
    assert abs(b.gap_slope(2.0) - b.J11 ** 2 / 4.0) < 1e-9
    assert abs(b.dimensionless_split_slope() - b.DISK_CHIH_SPLIT) < 1e-12


def test_not_inverse_or_spurious_factor():
    # guard against the common sign/factor errors
    assert abs(b.DISK_CHIH_SPLIT - (b.J01 / b.J11) ** 2) > 2.0   # not inverse
    assert b.DISK_CHIH_SPLIT > 2.5 and b.DISK_CHIH_SPLIT < 2.55  # not x2 / /2
    assert math.copysign(1.0, b.DISK_CHIH_SPLIT) > 0            # positive

"""Tests for symmetry-optimum explanation analysis helpers."""

from __future__ import annotations

import numpy as np

from src.inverse_screening import GeometryDiagnostics, compute_q
from src.symmetry_optimum_analysis import (
    IsoenergyPoint,
    classify_near_isotropy_optimum,
    classify_doublet_splitting,
    classify_symmetry_optimum,
    compute_s,
    finite_difference_signs,
    jaccard_overlap,
    local_refinement_candidates,
    local_extrema_indices,
    select_min_ekin_error_candidate,
    select_representative_points,
)


def test_q_and_s_computation() -> None:
    """Q and S should normalize gaps by Ekin."""
    ekin = np.array([0.01, 0.02])
    assert np.allclose(compute_q(np.array([0.015, 0.03]), ekin), np.array([1.5, 1.5]))
    assert np.allclose(compute_s(np.array([0.001, 0.004]), ekin), np.array([0.1, 0.2]))


def test_compute_s_rejects_nonpositive_ekin() -> None:
    """S is undefined when Ekin is not positive."""
    try:
        compute_s(np.array([0.1]), np.array([0.0]))
    except ValueError as exc:
        assert "Ekin must be positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError for nonpositive Ekin.")


def test_finite_difference_signs_with_tolerance() -> None:
    """Finite-difference signs should ignore tiny differences."""
    values = np.array([1.0, 1.1, 1.10000000001, 1.0])

    assert finite_difference_signs(values, tolerance=1e-8) == [1, 0, -1]


def test_local_extrema_indices() -> None:
    """Simple extrema detection should identify interior peaks and troughs."""
    values = np.array([1.0, 2.0, 1.0, 0.5, 0.7])

    assert local_extrema_indices(values) == [1, 3]


def test_classify_symmetry_optimum_supports_isotropic_largest_increasing() -> None:
    """Increasing Q with largest isotropic value should support the explanation."""
    ar = np.array([0.67, 0.75, 0.83, 0.94, 1.0])
    q = np.array([1.1, 1.2, 1.3, 1.4, 1.5])

    status, rho, signs, note = classify_symmetry_optimum(ar, q)

    assert status == "True"
    assert rho > 0.0
    assert signs == [1, 1, 1, 1]
    assert "mostly_increasing" in note


def test_classify_symmetry_optimum_rejects_noniso_winner() -> None:
    """A non-isotropic winner should reject the isotropic-optimum explanation."""
    ar = np.array([0.67, 0.75, 0.83, 0.94, 1.0])
    q = np.array([1.1, 1.2, 1.6, 1.4, 1.5])

    status, _, _, note = classify_symmetry_optimum(ar, q)

    assert status == "False"
    assert "nonisotropic" in note


def test_classify_symmetry_optimum_ambiguous_with_tiny_iso_advantage() -> None:
    """Near-ties should be classified conservatively as ambiguous."""
    ar = np.array([0.67, 0.75, 0.83, 0.94, 1.0])
    q = np.array([1.1, 1.2, 1.3, 1.4999999, 1.5])

    status, _, _, note = classify_symmetry_optimum(ar, q, tolerance=1e-5)

    assert status == "ambiguous"
    assert "within_tolerance" in note


def test_classify_doublet_splitting_supports_decrease_to_isotropy() -> None:
    """S decreasing as aspect_ratio approaches one supports doublet splitting."""
    ar = np.array([0.67, 0.75, 0.83, 0.94, 1.0])
    s = np.array([0.5, 0.4, 0.3, 0.2, 0.01])

    interpretation, rho, signs = classify_doublet_splitting(ar, s)

    assert interpretation.startswith("supports")
    assert rho < 0.0
    assert signs == [-1, -1, -1, -1]


def _point(ar: float, q: float, h: str) -> IsoenergyPoint:
    """Build a lightweight isoenergy point for representative selection tests."""
    geom = GeometryDiagnostics(h, 10, 5, 5, 0.0)
    return IsoenergyPoint(
        n=2.0,
        aspect_ratio=ar,
        a_root=30.0,
        b_root=30.0 * ar,
        ekin_target=0.01,
        ekin_pred=0.01,
        de1_pred=0.01 * q,
        de2_pred=0.001,
        q_pred=q,
        geometry=geom,
        failure_mode="ok",
    )


def test_select_representative_points_includes_nearest_and_extrema() -> None:
    """Representative selection should include requested nearest points and extrema."""
    points = [
        _point(0.67, 1.0, "a"),
        _point(0.75, 1.5, "b"),
        _point(0.83, 1.1, "c"),
        _point(0.89, 1.2, "d"),
        _point(0.94, 1.3, "e"),
        _point(1.00, 1.4, "f"),
    ]

    selected = select_representative_points(points, requested_aspect_ratios=(0.67, 0.83, 1.0))

    hashes = {point.geometry.geometry_hash for point in selected}
    assert {"a", "c", "f"}.issubset(hashes)
    assert "b" in hashes


def test_jaccard_overlap_for_geometry_sets() -> None:
    """Geometry comparison should expose exact and partial overlaps."""
    assert jaccard_overlap([(0, 0), (1, 0)], [(1, 0), (0, 0)]) == 1.0
    assert np.isclose(jaccard_overlap([(0, 0), (1, 0)], [(1, 0), (2, 0)]), 1.0 / 3.0)


def test_local_refinement_candidates_clip_and_sort_domain() -> None:
    """Local refinement candidates should stay inside the allowed domain."""
    out = local_refinement_candidates(
        24.1,
        deltas=(-0.3, -0.1, 0.0, 0.1, 0.3),
        a_min=24.0,
        a_max=36.0,
    )

    assert out == [24.0, 24.1, 24.2, 24.4]


def test_select_min_ekin_error_candidate() -> None:
    """Selection should minimize absolute Ekin error to the target."""
    rows = [
        {"label": "a", "Ekin_Kwant": 0.011},
        {"label": "b", "Ekin_Kwant": 0.0102},
        {"label": "c", "Ekin_Kwant": 0.009},
    ]

    selected = select_min_ekin_error_candidate(rows, ekin_target=0.010)

    assert selected["label"] == "b"


def test_classify_near_isotropy_optimum_supports_iso_largest() -> None:
    """Direct near-isotropy classification should support a clear isotropic optimum."""
    status, note = classify_near_isotropy_optimum(
        q_iso=1.5,
        best_noniso_q=1.45,
        spearman_q=1.0,
        tolerance=0.01,
    )

    assert status == "supports verified near-isotropy optimum"
    assert "isotropic_largest" in note


def test_classify_near_isotropy_optimum_flags_large_noniso_gain() -> None:
    """A non-isotropic Q gain above threshold should reject the explanation."""
    status, note = classify_near_isotropy_optimum(
        q_iso=1.5,
        best_noniso_q=1.54,
        spearman_q=0.8,
        tolerance=0.01,
    )

    assert status == "not supported"
    assert "nonisotropic" in note


def test_classify_near_isotropy_optimum_ambiguous_within_threshold() -> None:
    """Near ties should remain ambiguous."""
    status, note = classify_near_isotropy_optimum(
        q_iso=1.5,
        best_noniso_q=1.505,
        spearman_q=0.8,
        tolerance=0.01,
    )

    assert status == "ambiguous"
    assert "within_threshold" in note

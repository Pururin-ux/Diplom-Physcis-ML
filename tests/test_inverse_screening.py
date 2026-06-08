"""Unit tests for article inverse-screening helper logic."""

from __future__ import annotations

import numpy as np
from sklearn.dummy import DummyRegressor

from src import inverse_screening as inv


def test_physics_feature_matrix_values() -> None:
    """Article feature matrix should match the pre-registered basis."""
    a = np.array([10.0, 20.0])
    ar = np.array([1.0, 0.5])

    out = inv.physics_feature_matrix(a, ar)

    expected = np.column_stack([1.0 / (a**2), 1.0 / (a**2 * ar), ar])
    assert np.allclose(out, expected)


def test_compute_ekin_and_q() -> None:
    """Ekin and Q helpers should use the intended definitions."""
    e0 = np.array([-3.99, -3.98])
    de1 = np.array([0.01, 0.02])

    ekin = inv.compute_ekin(e0)
    q = inv.compute_q(de1, ekin)

    assert np.allclose(ekin, np.array([0.01, 0.02]))
    assert np.allclose(q, np.array([1.0, 1.0]))


def test_compute_q_rejects_nonpositive_ekin() -> None:
    """Q is undefined for nonpositive kinetic energy."""
    try:
        inv.compute_q(np.array([1.0]), np.array([0.0]))
    except ValueError as exc:
        assert "Ekin must be positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError for nonpositive Ekin.")


def test_find_ekin_root_no_root_handling() -> None:
    """Root finding should report no_root when signs do not bracket zero."""
    model = DummyRegressor(strategy="constant", constant=1.0)
    model.fit(np.ones((2, 3)), np.ones(2))

    root, status = inv.find_ekin_root(model, aspect_ratio=0.8, ekin_target=0.5)

    assert root is None
    assert status == "no_root"


def test_geometry_hash_stability() -> None:
    """Hashing should be independent of input coordinate order."""
    coords_a = [(1, 0), (0, 0), (0, 1)]
    coords_b = list(reversed(coords_a))

    assert inv.geometry_hash_from_coordinates(coords_a) == inv.geometry_hash_from_coordinates(coords_b)


def test_sublattice_counts() -> None:
    """Sublattice counts should follow parity of x+y."""
    coords = [(0, 0), (1, 0), (0, 1), (1, 1)]

    n_a, n_b = inv.sublattice_counts(coords)

    assert n_a == 2
    assert n_b == 2


def test_exact_training_grid_duplicate_detection() -> None:
    """Original-grid points should be labeled as training duplicates."""
    assert inv.is_exact_training_grid_duplicate(24.0, 0.67)
    assert not inv.is_exact_training_grid_duplicate(24.5, 0.67)
    assert not inv.is_exact_training_grid_duplicate(24.0, 0.675)


def _candidate(a: float, ar: float, q: float, h: str) -> inv.ScreeningCandidate:
    """Build a lightweight candidate for diversity tests."""
    geom = inv.GeometryDiagnostics(h, 100, 50, 50, 0.0)
    return inv.ScreeningCandidate(
        n=2.0,
        candidate_rank=None,
        candidate_type="inverse_candidate",
        a=a,
        b=a * ar,
        aspect_ratio=ar,
        ekin_target=0.01,
        ekin_pred=0.01,
        de1_pred=q * 0.01,
        q_pred=q,
        geometry=geom,
        failure_mode="ok",
    )


def test_select_diverse_top_candidates_filters_close_points() -> None:
    """Greedy selection should keep high-Q candidates but reject close duplicates."""
    candidates = [
        _candidate(30.0, 0.80, 2.0, "a"),
        _candidate(30.1, 0.801, 1.9, "b"),
        _candidate(33.0, 0.90, 1.8, "c"),
    ]

    selected = inv.select_diverse_top_candidates(candidates, max_count=5, min_distance=0.5)

    assert [item.geometry.geometry_hash for item in selected] == ["a", "c"]
    assert [item.candidate_rank for item in selected] == [1, 2]


def test_best_training_baseline_prefers_max_q_inside_ekin_constraint(monkeypatch) -> None:
    """Training baseline should choose best Q among feasible Kwant training rows."""
    monkeypatch.setattr(
        inv,
        "geometry_diagnostics",
        lambda a, b, n: inv.GeometryDiagnostics("hash", 10, 5, 5, 0.0),
    )
    rows = {
        "a": np.array([24.0, 27.0, 30.0]),
        "b": np.array([24.0, 27.0, 30.0]),
        "aspect_ratio": np.array([1.0, 1.0, 1.0]),
        "E0": np.array([-3.991, -3.990, -3.989]),
        "E1": np.array([-3.981, -3.975, -3.982]),
        "E2": np.array([-3.970, -3.960, -3.970]),
        "E3": np.array([-3.960, -3.950, -3.960]),
        "dE1": np.array([0.010, 0.015, 0.007]),
        "Ekin": np.array([0.009, 0.010, 0.011]),
        "Q": np.array([1.0, 1.5, 0.7]),
        "N_sites": np.array([1, 1, 1]),
    }

    out = inv.best_training_baseline(rows, n_value=2.0, ekin_target=0.010, epsilon_e=0.001)

    assert out.a == 27.0
    assert out.q_kwant == 1.5
    assert out.failure_mode == "ok"

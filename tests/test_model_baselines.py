"""Lightweight deterministic tests for non-neural baseline model utilities."""

from __future__ import annotations

import numpy as np

from src.model import (
    BASELINE_MODEL_NAMES,
    build_baseline_model,
    evaluate_ridge_feature_sets,
    evaluate_leave_one_group_out,
    make_physical_feature_matrix,
    make_ablation_feature_matrix,
    regression_metrics,
    run_baseline_stress_test,
    select_best_feature_set_by_mae,
)


def test_build_baseline_model_supported_names() -> None:
    """All declared model names should build successfully."""
    for name in BASELINE_MODEL_NAMES:
        model = build_baseline_model(name)
        assert model is not None


def test_regression_metrics_values() -> None:
    """Metric helper should return deterministic scalar values."""
    y_true = np.array([0.0, 1.0, 2.0], dtype=float)
    y_pred = np.array([0.0, 2.0, 2.0], dtype=float)
    m = regression_metrics(y_true, y_pred)
    assert np.isclose(m.mae, 1.0 / 3.0)
    assert np.isclose(m.rmse, np.sqrt(1.0 / 3.0))
    assert np.isclose(m.max_abs_error, 1.0)


def test_evaluate_leave_one_group_out_shapes() -> None:
    """Leave-one-group-out output should include expected keys and shapes."""
    X = np.array(
        [
            [1.0, 0.5],
            [2.0, 0.5],
            [3.0, 0.5],
            [1.0, 0.7],
            [2.0, 0.7],
            [3.0, 0.7],
        ],
        dtype=float,
    )
    y = 2.0 * X[:, 0] + 0.5 * X[:, 1]
    groups = X[:, 0]

    out = evaluate_leave_one_group_out(X, y, groups, model_name="ridge")
    assert set(out.keys()) == {"overall", "per_group", "y_true", "y_pred"}
    assert len(out["per_group"]) == len(np.unique(groups))
    assert out["y_true"].shape == y.shape
    assert out["y_pred"].shape == y.shape


def test_run_baseline_stress_test_protocol_keys() -> None:
    """Stress-test wrapper should expose LOAO and LOARO for each model."""
    X = np.array(
        [
            [1.0, 0.67],
            [2.0, 0.67],
            [3.0, 0.67],
            [1.0, 1.00],
            [2.0, 1.00],
            [3.0, 1.00],
        ],
        dtype=float,
    )
    y = X[:, 0] + X[:, 1]
    out = run_baseline_stress_test(X, y, a_values=X[:, 0], aspect_ratio_values=X[:, 1])

    for name in BASELINE_MODEL_NAMES:
        assert name in out
        assert set(out[name].keys()) == {"LOAO", "LOARO"}


def test_make_physical_feature_matrix_set_a_matches_raw_inputs() -> None:
    """Set A should preserve [a, aspect_ratio]."""
    a = np.array([24.0, 36.0], dtype=float)
    r = np.array([0.67, 1.00], dtype=float)
    X = make_physical_feature_matrix(a, r, feature_set="A")
    expected = np.column_stack([a, r])
    assert np.allclose(X, expected)


def test_make_physical_feature_matrix_set_b_and_c_inverse_forms() -> None:
    """Set B/C should apply inverse-size transforms deterministically."""
    a = np.array([10.0, 20.0], dtype=float)
    r = np.array([0.5, 1.0], dtype=float)

    Xb = make_physical_feature_matrix(a, r, feature_set="B")
    Xc = make_physical_feature_matrix(a, r, feature_set="C")

    expected_b = np.column_stack([1.0 / (a**2), r])
    expected_c = np.column_stack([1.0 / (a**2 * r), r])

    assert np.allclose(Xb, expected_b)
    assert np.allclose(Xc, expected_c)


def test_make_physical_feature_matrix_rejects_invalid_feature_set() -> None:
    """Unknown feature-set labels should fail fast."""
    a = np.array([24.0], dtype=float)
    r = np.array([1.0], dtype=float)
    try:
        make_physical_feature_matrix(a, r, feature_set="Z")
    except ValueError as exc:
        assert "Unsupported feature set" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported feature set.")


def test_make_ablation_feature_matrix_shapes_and_values() -> None:
    """Ablation matrix builder should correctly construct raw and physics-informed features."""
    a = np.array([10.0, 20.0], dtype=float)
    ar = np.array([1.0, 0.5], dtype=float)

    X_raw = make_ablation_feature_matrix(a, ar, feature_set="raw")
    expected_raw = np.column_stack([a, ar])
    assert np.allclose(X_raw, expected_raw)

    X_phys = make_ablation_feature_matrix(a, ar, feature_set="physics_informed")
    expected_phys = np.column_stack([1.0 / (a**2), 1.0 / (a**2 * ar), ar])
    assert np.allclose(X_phys, expected_phys)

    try:
        make_ablation_feature_matrix(a, ar, feature_set="unknown")
    except ValueError as exc:
        assert "Unsupported ablation feature set" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported ablation set.")


def test_evaluate_ridge_feature_sets_exposes_loao_and_loaro() -> None:
    """Ridge feature-set helper should return both protocols."""
    a = np.array([24.0, 27.0, 30.0, 24.0, 27.0, 30.0], dtype=float)
    r = np.array([0.67, 0.67, 0.67, 1.00, 1.00, 1.00], dtype=float)
    y = 4.0 + 0.2 * (1.0 / (a**2 * r))

    out = evaluate_ridge_feature_sets(a, r, y, feature_sets=("A", "B", "C"))
    assert set(out.keys()) == {"A", "B", "C"}
    for fs in ("A", "B", "C"):
        assert set(out[fs].keys()) == {"LOAO", "LOARO"}


def test_select_best_feature_set_by_mae_picks_lowest_mae() -> None:
    """Best-set selector should choose the minimum-MAE option."""
    feature_results = {
        "A": {"LOAO": {"overall": {"mae": 0.4, "rmse": 0.5, "max_abs_error": 0.8}}},
        "B": {"LOAO": {"overall": {"mae": 0.2, "rmse": 0.3, "max_abs_error": 0.6}}},
        "C": {"LOAO": {"overall": {"mae": 0.3, "rmse": 0.4, "max_abs_error": 0.7}}},
    }
    name, overall = select_best_feature_set_by_mae(feature_results, protocol="LOAO")
    assert name == "B"
    assert np.isclose(overall["mae"], 0.2)

"""Lightweight non-neural baseline utilities for tabular regression stress tests."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from sklearn.base import RegressorMixin
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.compose import TransformedTargetRegressor


BASELINE_MODEL_NAMES: tuple[str, ...] = (
    "linear",
    "ridge",
    "poly2_ridge",
    "knn",
    "mlp",
)

PHYSICAL_FEATURE_SET_NAMES: tuple[str, ...] = ("A", "B", "C")
ABLATION_FEATURE_SETS: tuple[str, ...] = ("raw", "physics_informed")


@dataclass(frozen=True)
class RegressionMetrics:
    """Absolute-error metrics used in baseline stress tests."""

    mae: float
    rmse: float
    max_abs_error: float


def build_baseline_model(name: str) -> RegressorMixin:
    """Build one supported non-neural baseline regressor by name."""
    if name == "linear":
        return LinearRegression()
    if name == "ridge":
        return Pipeline(
            steps=[
                ("scale", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        )
    if name == "poly2_ridge":
        return Pipeline(
            steps=[
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("scale", StandardScaler()),
                ("model", Ridge(alpha=1.0)),
            ]
        )
    if name == "knn":
        return Pipeline(
            steps=[
                ("scale", StandardScaler()),
                ("model", KNeighborsRegressor(n_neighbors=3)),
            ]
        )
    if name == "mlp":
        return TransformedTargetRegressor(
            regressor=Pipeline(
                steps=[
                    ("scale", StandardScaler()),
                    ("model", MLPRegressor(
                        hidden_layer_sizes=(16,),
                        activation="tanh",
                        solver="lbfgs",
                        alpha=1e-3,
                        early_stopping=False,
                        random_state=42,
                        max_iter=5000,
                 )),
                ]
        ),
        transformer=StandardScaler(),
    )
    raise ValueError(f"Unsupported baseline model: {name}")


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> RegressionMetrics:
    """Compute MAE, RMSE, and MaxAE from predictions."""
    err = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    abs_err = np.abs(err)
    return RegressionMetrics(
        mae=float(np.mean(abs_err)),
        rmse=float(np.sqrt(np.mean(err**2))),
        max_abs_error=float(np.max(abs_err)),
    )


def evaluate_leave_one_group_out(
    X: np.ndarray,
    y: np.ndarray,
    group_values: np.ndarray,
    model_name: str,
) -> dict[str, object]:
    """Evaluate one model under leave-one-group-out slicing."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    group_values = np.asarray(group_values)

    unique_groups = np.unique(group_values)
    if unique_groups.size < 2:
        raise ValueError("Need at least two unique groups for leave-one-group-out.")

    y_true_all: list[np.ndarray] = []
    y_pred_all: list[np.ndarray] = []
    per_group: list[dict[str, float]] = []

    for g in unique_groups:
        test_mask = group_values == g
        train_mask = ~test_mask
        model = build_baseline_model(model_name)
        model.fit(X[train_mask], y[train_mask])
        pred = np.asarray(model.predict(X[test_mask]), dtype=float)

        fold_metrics = regression_metrics(y[test_mask], pred)
        per_group.append(
            {
                "group": float(g),
                "mae": fold_metrics.mae,
                "rmse": fold_metrics.rmse,
                "max_abs_error": fold_metrics.max_abs_error,
            }
        )
        y_true_all.append(y[test_mask])
        y_pred_all.append(pred)

    y_true_concat = np.concatenate(y_true_all)
    y_pred_concat = np.concatenate(y_pred_all)
    overall = regression_metrics(y_true_concat, y_pred_concat)
    return {
        "overall": {
            "mae": overall.mae,
            "rmse": overall.rmse,
            "max_abs_error": overall.max_abs_error,
        },
        "per_group": per_group,
        "y_true": y_true_concat,
        "y_pred": y_pred_concat,
    }


def run_baseline_stress_test(
    X: np.ndarray,
    y: np.ndarray,
    a_values: np.ndarray,
    aspect_ratio_values: np.ndarray,
    model_names: Iterable[str] = BASELINE_MODEL_NAMES,
) -> dict[str, dict[str, dict[str, object]]]:
    """Run LOAO and LOARO evaluations for each baseline model."""
    results: dict[str, dict[str, dict[str, object]]] = {}
    for model_name in model_names:
        results[model_name] = {
            "LOAO": evaluate_leave_one_group_out(X, y, a_values, model_name),
            "LOARO": evaluate_leave_one_group_out(X, y, aspect_ratio_values, model_name),
        }
    return results


def make_physical_feature_matrix(
    a_values: np.ndarray,
    aspect_ratio_values: np.ndarray,
    feature_set: str,
) -> np.ndarray:
    """Build one of the predeclared physical feature sets for ablation.

    Feature sets:
    - A: [a, aspect_ratio]
    - B: [1/a^2, aspect_ratio]
    - C: [1/(a^2 * aspect_ratio), aspect_ratio]
    """
    a = np.asarray(a_values, dtype=float)
    ar = np.asarray(aspect_ratio_values, dtype=float)
    if a.shape != ar.shape:
        raise ValueError("a_values and aspect_ratio_values must have identical shapes.")
    if np.any(a <= 0.0):
        raise ValueError("All a_values must be strictly positive.")
    if np.any(ar <= 0.0):
        raise ValueError("All aspect_ratio_values must be strictly positive.")

    if feature_set == "A":
        first_feature = a
    elif feature_set == "B":
        first_feature = 1.0 / (a**2)
    elif feature_set == "C":
        first_feature = 1.0 / (a**2 * ar)
    else:
        raise ValueError(
            f"Unsupported feature set: {feature_set}. "
            f"Supported values: {PHYSICAL_FEATURE_SET_NAMES}"
        )

    return np.column_stack([first_feature, ar])


def make_ablation_feature_matrix(
    a_values: np.ndarray,
    aspect_ratio_values: np.ndarray,
    feature_set: str,
) -> np.ndarray:
    """Build predefined feature sets for the MLP vs Ridge ablation study."""
    a = np.asarray(a_values, dtype=float)
    ar = np.asarray(aspect_ratio_values, dtype=float)

    if a.shape != ar.shape:
        raise ValueError("a_values and aspect_ratio_values must have identical shapes.")

    if feature_set == "raw":
        return np.column_stack([a, ar])
    elif feature_set == "physics_informed":
        return np.column_stack([1.0 / (a**2), 1.0 / (a**2 * ar), ar])
    else:
        raise ValueError(
            f"Unsupported ablation feature set: {feature_set}. "
            f"Supported values: {ABLATION_FEATURE_SETS}"
        )


def evaluate_ridge_feature_sets(
    a_values: np.ndarray,
    aspect_ratio_values: np.ndarray,
    y_values: np.ndarray,
    feature_sets: Iterable[str] = PHYSICAL_FEATURE_SET_NAMES,
) -> dict[str, dict[str, object]]:
    """Evaluate Ridge under LOAO/LOARO for each declared feature set."""
    a = np.asarray(a_values, dtype=float)
    ar = np.asarray(aspect_ratio_values, dtype=float)
    y = np.asarray(y_values, dtype=float)
    if not (a.shape == ar.shape == y.shape):
        raise ValueError("a_values, aspect_ratio_values, and y_values must share shape.")

    out: dict[str, dict[str, object]] = {}
    for feature_set in feature_sets:
        X = make_physical_feature_matrix(a, ar, feature_set=feature_set)
        out[str(feature_set)] = {
            "LOAO": evaluate_leave_one_group_out(X, y, a, model_name="ridge"),
            "LOARO": evaluate_leave_one_group_out(X, y, ar, model_name="ridge"),
        }
    return out


def select_best_feature_set_by_mae(
    feature_results: dict[str, dict[str, object]],
    protocol: str,
) -> tuple[str, dict[str, float]]:
    """Pick the best feature set for one protocol by lowest MAE."""
    best_name: str | None = None
    best_overall: dict[str, float] | None = None
    best_mae = np.inf
    for feature_set, protocol_results in feature_results.items():
        overall = protocol_results[protocol]["overall"]
        mae = float(overall["mae"])
        if mae < best_mae:
            best_mae = mae
            best_name = feature_set
            best_overall = {
                "mae": float(overall["mae"]),
                "rmse": float(overall["rmse"]),
                "max_abs_error": float(overall["max_abs_error"]),
            }

    if best_name is None or best_overall is None:
        raise ValueError("feature_results must include at least one feature set.")
    return best_name, best_overall

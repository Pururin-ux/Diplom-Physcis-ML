"""Analyze whether isotropic superellipses explain inverse-screening failure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.stats import spearmanr

from .dataset import DatasetDict, _superellipse_levels_and_site_count
from .geometry import build_superellipse_dot
from .inverse_screening import (
    GeometryDiagnostics,
    compute_ekin,
    compute_q,
    find_ekin_root,
    geometry_diagnostics,
    load_superellipse_dataset,
    physics_feature_matrix,
    site_coordinates_from_system,
    train_surrogates_for_n,
)
from .model import build_baseline_model


REPRESENTATIVE_ASPECT_RATIOS = (0.67, 0.75, 0.83, 0.89, 0.94, 1.0)


@dataclass(frozen=True)
class IsoenergyPoint:
    """One point on a surrogate iso-``Ekin`` curve."""

    n: float
    aspect_ratio: float
    a_root: float
    b_root: float
    ekin_target: float
    ekin_pred: float
    de1_pred: float
    de2_pred: float
    q_pred: float
    geometry: GeometryDiagnostics
    failure_mode: str
    requested_aspect_ratio: float | None = None


@dataclass(frozen=True)
class KwantVerification:
    """Direct Kwant spectrum and derived diagnostics for an isoenergy point."""

    e0: float
    e1: float
    e2: float
    e3: float
    ekin: float
    de1: float
    de2: float
    q: float
    s: float
    failure_mode: str


def compute_s(de2_values: np.ndarray | float, ekin_values: np.ndarray | float) -> np.ndarray | float:
    """Return normalized first-excited-doublet splitting ``S = dE2 / Ekin``."""
    de2 = np.asarray(de2_values, dtype=float)
    ekin = np.asarray(ekin_values, dtype=float)
    if np.any(ekin <= 0.0):
        raise ValueError("Ekin must be positive to compute S.")
    return de2 / ekin


def train_de2_surrogate_for_n(dataset: DatasetDict, n_value: float) -> object:
    """Train the same Ridge model family for diagnostic ``dE2`` predictions."""
    n_arr = np.asarray(dataset["n"], dtype=float)
    mask = np.isclose(n_arr, n_value)
    if int(np.sum(mask)) == 0:
        raise ValueError(f"No dataset rows for n={n_value}.")
    a = np.asarray(dataset["a"], dtype=float)[mask]
    ar = np.asarray(dataset["aspect_ratio"], dtype=float)[mask]
    de2 = np.asarray(dataset["dE2"], dtype=float)[mask]
    model = build_baseline_model("ridge")
    model.fit(physics_feature_matrix(a, ar), de2)
    return model


def generate_isoenergy_curve_for_n(
    dataset: DatasetDict,
    n_value: float,
    aspect_ratio_grid: np.ndarray,
) -> tuple[list[IsoenergyPoint], list[dict[str, object]], float]:
    """Generate deduplicated surrogate iso-``Ekin`` curve rows for one ``n``."""
    model_ekin, model_de1, training_rows = train_surrogates_for_n(dataset, n_value)
    model_de2 = train_de2_surrogate_for_n(dataset, n_value)
    ekin_target = float(np.median(training_rows["Ekin"]))
    points: list[IsoenergyPoint] = []
    audit_rows: list[dict[str, object]] = []
    seen_hashes: set[str] = set()

    for ar_value in aspect_ratio_grid:
        ar = float(ar_value)
        root, status = find_ekin_root(model_ekin, ar, ekin_target)
        base = {
            "n": n_value,
            "aspect_ratio": ar,
            "a_root": np.nan if root is None else root,
            "failure_mode": status,
        }
        if root is None or status != "ok":
            audit_rows.append(base)
            continue

        b_root = float(root * ar)
        x = physics_feature_matrix(np.array([root]), np.array([ar]))
        ekin_pred = float(model_ekin.predict(x)[0])
        de1_pred = float(model_de1.predict(x)[0])
        de2_pred = float(model_de2.predict(x)[0])
        q_pred = float(compute_q(de1_pred, ekin_pred))
        geom = geometry_diagnostics(a=float(root), b=b_root, n=n_value)
        if geom.geometry_hash in seen_hashes:
            audit_rows.append(
                {
                    **base,
                    "b_root": b_root,
                    "Ekin_pred": ekin_pred,
                    "dE1_pred": de1_pred,
                    "dE2_pred": de2_pred,
                    "Q_pred": q_pred,
                    "geometry_hash": geom.geometry_hash,
                    "failure_mode": "duplicate_candidate_geometry",
                }
            )
            continue
        seen_hashes.add(geom.geometry_hash)
        point = IsoenergyPoint(
            n=n_value,
            aspect_ratio=ar,
            a_root=float(root),
            b_root=b_root,
            ekin_target=ekin_target,
            ekin_pred=ekin_pred,
            de1_pred=de1_pred,
            de2_pred=de2_pred,
            q_pred=q_pred,
            geometry=geom,
            failure_mode="ok",
        )
        points.append(point)
        audit_rows.append(
            {
                **base,
                "b_root": b_root,
                "Ekin_pred": ekin_pred,
                "dE1_pred": de1_pred,
                "dE2_pred": de2_pred,
                "Q_pred": q_pred,
                "geometry_hash": geom.geometry_hash,
                "failure_mode": "ok",
            }
        )

    return points, audit_rows, ekin_target


def local_extrema_indices(values: np.ndarray) -> list[int]:
    """Return indices of simple one-dimensional local extrema."""
    arr = np.asarray(values, dtype=float)
    if arr.size < 3:
        return []
    out: list[int] = []
    for idx in range(1, arr.size - 1):
        prev_v = arr[idx - 1]
        cur_v = arr[idx]
        next_v = arr[idx + 1]
        if (cur_v > prev_v and cur_v > next_v) or (cur_v < prev_v and cur_v < next_v):
            out.append(idx)
    return out


def select_representative_points(
    points: list[IsoenergyPoint],
    requested_aspect_ratios: Iterable[float] = REPRESENTATIVE_ASPECT_RATIOS,
) -> list[IsoenergyPoint]:
    """Select requested aspect-ratio representatives plus surrogate extrema."""
    if not points:
        return []

    selected_indices: set[int] = set()
    ar_values = np.array([point.aspect_ratio for point in points], dtype=float)
    q_values = np.array([point.q_pred for point in points], dtype=float)

    for requested in requested_aspect_ratios:
        idx = int(np.argmin(np.abs(ar_values - float(requested))))
        selected_indices.add(idx)

    for idx in local_extrema_indices(q_values):
        selected_indices.add(idx)

    selected: list[IsoenergyPoint] = []
    for idx in sorted(selected_indices, key=lambda item: ar_values[item]):
        point = points[idx]
        requested = min(requested_aspect_ratios, key=lambda value: abs(value - point.aspect_ratio))
        selected.append(
            IsoenergyPoint(
                n=point.n,
                aspect_ratio=point.aspect_ratio,
                a_root=point.a_root,
                b_root=point.b_root,
                ekin_target=point.ekin_target,
                ekin_pred=point.ekin_pred,
                de1_pred=point.de1_pred,
                de2_pred=point.de2_pred,
                q_pred=point.q_pred,
                geometry=point.geometry,
                failure_mode=point.failure_mode,
                requested_aspect_ratio=float(requested),
            )
        )
    return selected


def verify_isoenergy_point(point: IsoenergyPoint) -> KwantVerification:
    """Run direct Kwant verification for one isoenergy point."""
    try:
        vals, _ = _superellipse_levels_and_site_count(a=point.a_root, b=point.b_root, n=point.n)
        e0, e1, e2, e3 = [float(v) for v in vals]
        ekin = float(compute_ekin(e0))
        de1 = e1 - e0
        de2 = e2 - e1
        return KwantVerification(
            e0=e0,
            e1=e1,
            e2=e2,
            e3=e3,
            ekin=ekin,
            de1=de1,
            de2=de2,
            q=float(compute_q(de1, ekin)),
            s=float(compute_s(de2, ekin)),
            failure_mode="ok",
        )
    except Exception:
        return KwantVerification(
            e0=np.nan,
            e1=np.nan,
            e2=np.nan,
            e3=np.nan,
            ekin=np.nan,
            de1=np.nan,
            de2=np.nan,
            q=np.nan,
            s=np.nan,
            failure_mode="kwant_failure",
        )


def finite_difference_signs(values: np.ndarray, tolerance: float = 1e-10) -> list[int]:
    """Return signs of adjacent differences, ignoring tiny numerical changes."""
    arr = np.asarray(values, dtype=float)
    signs: list[int] = []
    for diff in np.diff(arr):
        if diff > tolerance:
            signs.append(1)
        elif diff < -tolerance:
            signs.append(-1)
        else:
            signs.append(0)
    return signs


def classify_symmetry_optimum(
    aspect_ratios: np.ndarray,
    q_values: np.ndarray,
    tolerance: float = 1e-6,
) -> tuple[str, float, list[int], str]:
    """Classify whether verified Q values support an isotropic optimum."""
    ar = np.asarray(aspect_ratios, dtype=float)
    q = np.asarray(q_values, dtype=float)
    mask = np.isfinite(ar) & np.isfinite(q)
    ar = ar[mask]
    q = q[mask]
    if q.size < 3:
        return "ambiguous", np.nan, [], "fewer_than_three_verified_points"

    order = np.argsort(ar)
    ar = ar[order]
    q = q[order]
    rho = float(spearmanr(ar, q).statistic)
    signs = finite_difference_signs(q, tolerance=tolerance)
    iso_idx = int(np.argmax(ar))
    q_iso = float(q[iso_idx])
    noniso = q[ar < ar[iso_idx]]
    if noniso.size == 0:
        return "ambiguous", rho, signs, "no_nonisotropic_verified_points"

    best_noniso = float(np.max(noniso))
    positive_fraction = sum(1 for sign in signs if sign > 0) / len(signs) if signs else 0.0
    if best_noniso > q_iso + tolerance:
        return "False", rho, signs, "nonisotropic_point_beats_isotropic"
    if q_iso - best_noniso <= tolerance:
        return "ambiguous", rho, signs, "isotropic_advantage_within_tolerance"
    if positive_fraction >= 0.75 and rho > 0.0:
        return "True", rho, signs, "isotropic_largest_and_mostly_increasing"
    return "ambiguous", rho, signs, "isotropic_largest_but_trend_not_monotone"


def classify_doublet_splitting(
    aspect_ratios: np.ndarray,
    s_values: np.ndarray,
    tolerance: float = 1e-6,
) -> tuple[str, float, list[int]]:
    """Classify whether normalized splitting decreases toward isotropy."""
    ar = np.asarray(aspect_ratios, dtype=float)
    s = np.asarray(s_values, dtype=float)
    mask = np.isfinite(ar) & np.isfinite(s)
    ar = ar[mask]
    s = s[mask]
    if s.size < 3:
        return "ambiguous: fewer than three verified points", np.nan, []

    order = np.argsort(ar)
    ar = ar[order]
    s = s[order]
    rho = float(spearmanr(ar, s).statistic)
    signs = finite_difference_signs(s, tolerance=tolerance)
    iso_s = float(s[np.argmax(ar)])
    noniso = s[ar < np.max(ar)]
    if noniso.size == 0:
        return "ambiguous: no non-isotropic verified points", rho, signs
    if np.any(noniso < iso_s - tolerance):
        return "not supported: a non-isotropic point has smaller splitting than isotropic", rho, signs
    negative_fraction = sum(1 for sign in signs if sign < 0) / len(signs) if signs else 0.0
    if negative_fraction >= 0.75 and rho < 0.0:
        return "supports: splitting decreases toward isotropy", rho, signs
    return "ambiguous: isotropic splitting small but trend is not monotone", rho, signs


def jaccard_overlap(coords_a: Iterable[tuple[int, int]], coords_b: Iterable[tuple[int, int]]) -> float:
    """Return Jaccard overlap between two coordinate sets."""
    set_a = set(coords_a)
    set_b = set(coords_b)
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)


def site_coordinates_for_superellipse(a: float, b: float, n: float) -> list[tuple[int, int]]:
    """Return sorted site coordinates for one superellipse geometry."""
    return site_coordinates_from_system(build_superellipse_dot(a=a, b=b, n=n))


def load_dataset(path: str) -> DatasetDict:
    """Compatibility wrapper for loading the dense superellipse dataset."""
    return load_superellipse_dataset(path)

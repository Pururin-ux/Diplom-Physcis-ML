"""One-shot surrogate-guided inverse screening for superellipse spectra.

This module treats Ridge predictions only as candidate generators. Reported
physical quantities are accepted only after direct Kwant verification.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.optimize import brentq

from .dataset import DatasetDict, _superellipse_levels_and_site_count
from .geometry import build_superellipse_dot
from .model import build_baseline_model, make_ablation_feature_matrix


MAIN_A_MIN = 24.0
MAIN_A_MAX = 36.0
MAIN_AR_MIN = 0.67
MAIN_AR_MAX = 1.0
MAIN_N_VALUES = (1.2, 2.0, 3.0, 4.0)
TRAINING_A_VALUES = (24.0, 27.0, 30.0, 33.0, 36.0)
TRAINING_AR_VALUES = (0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0)


@dataclass(frozen=True)
class GeometryDiagnostics:
    """Discrete diagnostics for a finalized Kwant lattice domain."""

    geometry_hash: str
    n_sites: int
    n_a: int
    n_b: int
    imbalance_ratio: float


@dataclass(frozen=True)
class ScreeningCandidate:
    """Continuous surrogate candidate plus discrete geometry diagnostics."""

    n: float
    candidate_rank: int | None
    candidate_type: str
    a: float
    b: float
    aspect_ratio: float
    ekin_target: float
    ekin_pred: float
    de1_pred: float
    q_pred: float
    geometry: GeometryDiagnostics
    failure_mode: str


@dataclass(frozen=True)
class VerifiedRow:
    """A candidate or baseline with direct Kwant values where available."""

    n: float
    candidate_rank: int | None
    candidate_type: str
    a: float
    b: float
    aspect_ratio: float
    ekin_target: float
    ekin_pred: float
    de1_pred: float
    q_pred: float
    e0_kwant: float
    e1_kwant: float
    e2_kwant: float
    e3_kwant: float
    ekin_kwant: float
    de1_kwant: float
    q_kwant: float
    ekin_error: float
    de1_error: float
    q_error: float
    passes_ekin_constraint_pred: bool
    passes_ekin_constraint_kwant: bool
    geometry_hash: str
    n_sites: int
    n_a: int
    n_b: int
    imbalance_ratio: float
    failure_mode: str


def compute_ekin(e0_values: np.ndarray | float) -> np.ndarray | float:
    """Return kinetic energy relative to the square-lattice band bottom."""
    return np.asarray(e0_values) + 4.0


def compute_q(de1_values: np.ndarray | float, ekin_values: np.ndarray | float) -> np.ndarray | float:
    """Return the relative first-gap objective ``Q = dE1 / Ekin``."""
    de1 = np.asarray(de1_values, dtype=float)
    ekin = np.asarray(ekin_values, dtype=float)
    if np.any(ekin <= 0.0):
        raise ValueError("Ekin must be positive to compute Q.")
    return de1 / ekin


def physics_feature_matrix(a_values: np.ndarray, aspect_ratio_values: np.ndarray) -> np.ndarray:
    """Build the article-screening physics-informed feature matrix."""
    return make_ablation_feature_matrix(
        np.asarray(a_values, dtype=float),
        np.asarray(aspect_ratio_values, dtype=float),
        feature_set="physics_informed",
    )


def site_coordinates_from_system(fsys: object) -> list[tuple[int, int]]:
    """Return sorted integer lattice coordinates for a finalized Kwant system."""
    coords = [(int(site.tag[0]), int(site.tag[1])) for site in fsys.sites]
    coords.sort()
    return coords


def geometry_hash_from_coordinates(coords: Iterable[tuple[int, int]]) -> str:
    """Return a stable hash of sorted integer site coordinates."""
    h = hashlib.sha256()
    for x, y in sorted(coords):
        h.update(f"{int(x)},{int(y)};".encode("ascii"))
    return h.hexdigest()


def sublattice_counts(coords: Iterable[tuple[int, int]]) -> tuple[int, int]:
    """Count square-lattice A/B sites using parity of ``x + y``."""
    n_a = 0
    n_b = 0
    for x, y in coords:
        if (int(x) + int(y)) % 2 == 0:
            n_a += 1
        else:
            n_b += 1
    return n_a, n_b


def geometry_diagnostics(a: float, b: float, n: float) -> GeometryDiagnostics:
    """Build a superellipse and return discrete geometry diagnostics."""
    fsys = build_superellipse_dot(a=a, b=b, n=n)
    coords = site_coordinates_from_system(fsys)
    n_a, n_b = sublattice_counts(coords)
    n_sites = len(coords)
    imbalance = abs(n_a - n_b) / n_sites if n_sites else np.nan
    return GeometryDiagnostics(
        geometry_hash=geometry_hash_from_coordinates(coords),
        n_sites=n_sites,
        n_a=n_a,
        n_b=n_b,
        imbalance_ratio=float(imbalance),
    )


def find_ekin_root(
    model: object,
    aspect_ratio: float,
    ekin_target: float,
    a_min: float = MAIN_A_MIN,
    a_max: float = MAIN_A_MAX,
) -> tuple[float | None, str]:
    """Find ``a`` where predicted Ekin matches the target for one aspect ratio."""

    def objective(a_value: float) -> float:
        x = physics_feature_matrix(np.array([a_value]), np.array([aspect_ratio]))
        return float(model.predict(x)[0]) - ekin_target

    f_min = objective(a_min)
    f_max = objective(a_max)
    if not (np.isfinite(f_min) and np.isfinite(f_max)):
        return None, "nonfinite_prediction"
    if f_min == 0.0:
        return a_min, "ok"
    if f_max == 0.0:
        return a_max, "ok"
    if f_min * f_max > 0.0:
        return None, "no_root"

    root = float(brentq(objective, a_min, a_max))
    if root < a_min or root > a_max:
        return root, "out_of_domain_root"
    return root, "ok"


def is_exact_training_grid_duplicate(a: float, aspect_ratio: float, atol: float = 1e-8) -> bool:
    """Return whether continuous parameters coincide with the original grid."""
    return any(np.isclose(a, x, atol=atol, rtol=0.0) for x in TRAINING_A_VALUES) and any(
        np.isclose(aspect_ratio, x, atol=atol, rtol=0.0) for x in TRAINING_AR_VALUES
    )


def select_diverse_top_candidates(
    candidates: list[ScreeningCandidate],
    max_count: int = 5,
    min_distance: float = 0.5,
) -> list[ScreeningCandidate]:
    """Greedily select top predicted-Q candidates with simple geometry diversity."""
    selected: list[ScreeningCandidate] = []
    for cand in sorted(candidates, key=lambda item: item.q_pred, reverse=True):
        is_diverse = True
        for prev in selected:
            distance = np.sqrt(
                ((cand.a - prev.a) / 3.0) ** 2
                + ((cand.aspect_ratio - prev.aspect_ratio) / 0.05) ** 2
            )
            if distance <= min_distance:
                is_diverse = False
                break
        if is_diverse:
            selected.append(cand)
        if len(selected) >= max_count:
            break
    return [
        ScreeningCandidate(
            n=c.n,
            candidate_rank=i + 1,
            candidate_type=c.candidate_type,
            a=c.a,
            b=c.b,
            aspect_ratio=c.aspect_ratio,
            ekin_target=c.ekin_target,
            ekin_pred=c.ekin_pred,
            de1_pred=c.de1_pred,
            q_pred=c.q_pred,
            geometry=c.geometry,
            failure_mode=c.failure_mode,
        )
        for i, c in enumerate(selected)
    ]


def train_surrogates_for_n(dataset: DatasetDict, n_value: float) -> tuple[object, object, dict[str, np.ndarray]]:
    """Train Ridge surrogates for Ekin and dE1 inside one fixed ``n`` class."""
    n_arr = np.asarray(dataset["n"], dtype=float)
    mask = np.isclose(n_arr, n_value)
    if int(np.sum(mask)) == 0:
        raise ValueError(f"No dataset rows for n={n_value}.")

    a = np.asarray(dataset["a"], dtype=float)[mask]
    ar = np.asarray(dataset["aspect_ratio"], dtype=float)[mask]
    e0 = np.asarray(dataset["E0"], dtype=float)[mask]
    de1 = np.asarray(dataset["dE1"], dtype=float)[mask]
    x = physics_feature_matrix(a, ar)

    model_ekin = build_baseline_model("ridge")
    model_de1 = build_baseline_model("ridge")
    model_ekin.fit(x, compute_ekin(e0))
    model_de1.fit(x, de1)

    rows = {
        "a": a,
        "aspect_ratio": ar,
        "b": np.asarray(dataset["b"], dtype=float)[mask],
        "E0": e0,
        "E1": np.asarray(dataset["E1"], dtype=float)[mask],
        "E2": np.asarray(dataset["E2"], dtype=float)[mask],
        "E3": np.asarray(dataset["E3"], dtype=float)[mask],
        "dE1": de1,
        "Ekin": np.asarray(compute_ekin(e0), dtype=float),
        "Q": np.asarray(compute_q(de1, compute_ekin(e0)), dtype=float),
        "N_sites": np.asarray(dataset["N_sites"], dtype=int)[mask],
    }
    return model_ekin, model_de1, rows


def generate_candidate_pool_for_n(
    dataset: DatasetDict,
    n_value: float,
    aspect_ratio_grid: np.ndarray,
) -> tuple[list[ScreeningCandidate], list[dict[str, object]], float, object, object, dict[str, np.ndarray]]:
    """Generate and deduplicate off-grid surrogate candidates for one ``n`` class."""
    model_ekin, model_de1, rows = train_surrogates_for_n(dataset, n_value)
    ekin_target = float(np.median(rows["Ekin"]))
    pool: list[ScreeningCandidate] = []
    audit_rows: list[dict[str, object]] = []
    seen_hashes: set[str] = set()

    for ar in aspect_ratio_grid:
        root, status = find_ekin_root(model_ekin, float(ar), ekin_target)
        audit_base: dict[str, object] = {
            "n": n_value,
            "aspect_ratio": float(ar),
            "a": np.nan if root is None else root,
            "failure_mode": status,
        }
        if root is None or status != "ok":
            audit_rows.append(audit_base)
            continue
        if is_exact_training_grid_duplicate(root, float(ar)):
            audit_rows.append({**audit_base, "failure_mode": "duplicate_training_geometry"})
            continue

        b = root * float(ar)
        x = physics_feature_matrix(np.array([root]), np.array([float(ar)]))
        ekin_pred = float(model_ekin.predict(x)[0])
        de1_pred = float(model_de1.predict(x)[0])
        q_pred = float(compute_q(de1_pred, ekin_pred))
        geom = geometry_diagnostics(a=root, b=b, n=n_value)

        if geom.geometry_hash in seen_hashes:
            audit_rows.append(
                {
                    **audit_base,
                    "b": b,
                    "Ekin_pred": ekin_pred,
                    "dE1_pred": de1_pred,
                    "Q_pred": q_pred,
                    "geometry_hash": geom.geometry_hash,
                    "failure_mode": "duplicate_candidate_geometry",
                }
            )
            continue
        seen_hashes.add(geom.geometry_hash)
        cand = ScreeningCandidate(
            n=n_value,
            candidate_rank=None,
            candidate_type="inverse_candidate",
            a=root,
            b=b,
            aspect_ratio=float(ar),
            ekin_target=ekin_target,
            ekin_pred=ekin_pred,
            de1_pred=de1_pred,
            q_pred=q_pred,
            geometry=geom,
            failure_mode="ok",
        )
        pool.append(cand)
        audit_rows.append(
            {
                **audit_base,
                "b": b,
                "Ekin_pred": ekin_pred,
                "dE1_pred": de1_pred,
                "Q_pred": q_pred,
                "geometry_hash": geom.geometry_hash,
                "N_sites": geom.n_sites,
                "N_A": geom.n_a,
                "N_B": geom.n_b,
                "imbalance_ratio": geom.imbalance_ratio,
                "failure_mode": "ok",
            }
        )

    return pool, audit_rows, ekin_target, model_ekin, model_de1, rows


def verify_candidate(cand: ScreeningCandidate, epsilon_e: float) -> VerifiedRow:
    """Compute direct Kwant energies and errors for one candidate."""
    try:
        vals, _ = _superellipse_levels_and_site_count(a=cand.a, b=cand.b, n=cand.n)
        e0, e1, e2, e3 = [float(v) for v in vals]
        ekin_kwant = float(compute_ekin(e0))
        de1_kwant = e1 - e0
        q_kwant = float(compute_q(de1_kwant, ekin_kwant))
        failure_mode = cand.failure_mode
        passes_kwant = abs(ekin_kwant - cand.ekin_target) <= epsilon_e
        if failure_mode == "ok" and not passes_kwant:
            failure_mode = "predicted_feasible_but_kwant_failed_E_constraint"
    except Exception:
        e0 = e1 = e2 = e3 = np.nan
        ekin_kwant = de1_kwant = q_kwant = np.nan
        passes_kwant = False
        failure_mode = "kwant_failure"

    return VerifiedRow(
        n=cand.n,
        candidate_rank=cand.candidate_rank,
        candidate_type=cand.candidate_type,
        a=cand.a,
        b=cand.b,
        aspect_ratio=cand.aspect_ratio,
        ekin_target=cand.ekin_target,
        ekin_pred=cand.ekin_pred,
        de1_pred=cand.de1_pred,
        q_pred=cand.q_pred,
        e0_kwant=e0,
        e1_kwant=e1,
        e2_kwant=e2,
        e3_kwant=e3,
        ekin_kwant=ekin_kwant,
        de1_kwant=de1_kwant,
        q_kwant=q_kwant,
        ekin_error=abs(ekin_kwant - cand.ekin_pred),
        de1_error=abs(de1_kwant - cand.de1_pred),
        q_error=abs(q_kwant - cand.q_pred),
        passes_ekin_constraint_pred=abs(cand.ekin_pred - cand.ekin_target) <= epsilon_e,
        passes_ekin_constraint_kwant=passes_kwant,
        geometry_hash=cand.geometry.geometry_hash,
        n_sites=cand.geometry.n_sites,
        n_a=cand.geometry.n_a,
        n_b=cand.geometry.n_b,
        imbalance_ratio=cand.geometry.imbalance_ratio,
        failure_mode=failure_mode,
    )


def make_surrogate_candidate(
    n_value: float,
    candidate_type: str,
    a: float,
    aspect_ratio: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
    rank: int | None = None,
) -> ScreeningCandidate:
    """Create one candidate row with surrogate predictions and geometry diagnostics."""
    b = float(a) * float(aspect_ratio)
    x = physics_feature_matrix(np.array([a]), np.array([aspect_ratio]))
    ekin_pred = float(model_ekin.predict(x)[0])
    de1_pred = float(model_de1.predict(x)[0])
    return ScreeningCandidate(
        n=n_value,
        candidate_rank=rank,
        candidate_type=candidate_type,
        a=float(a),
        b=b,
        aspect_ratio=float(aspect_ratio),
        ekin_target=ekin_target,
        ekin_pred=ekin_pred,
        de1_pred=de1_pred,
        q_pred=float(compute_q(de1_pred, ekin_pred)),
        geometry=geometry_diagnostics(a=float(a), b=b, n=n_value),
        failure_mode="ok",
    )


def isotropic_same_n_baseline(
    n_value: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
) -> ScreeningCandidate | None:
    """Return the same-``n`` isotropic baseline root, if feasible."""
    root, status = find_ekin_root(model_ekin, MAIN_AR_MAX, ekin_target)
    if root is None or status != "ok":
        return None
    return make_surrogate_candidate(
        n_value=n_value,
        candidate_type="isotropic_same_n_baseline",
        a=root,
        aspect_ratio=MAIN_AR_MAX,
        ekin_target=ekin_target,
        model_ekin=model_ekin,
        model_de1=model_de1,
    )


def best_training_baseline(
    rows: dict[str, np.ndarray],
    n_value: float,
    ekin_target: float,
    epsilon_e: float,
) -> VerifiedRow:
    """Select the best already Kwant-computed training baseline for one ``n``."""
    q = np.asarray(rows["Q"], dtype=float)
    ekin = np.asarray(rows["Ekin"], dtype=float)
    feasible = np.abs(ekin - ekin_target) <= epsilon_e
    if np.any(feasible):
        local_indices = np.flatnonzero(feasible)
        chosen = int(local_indices[np.argmax(q[feasible])])
        failure_mode = "ok"
    else:
        sigma_e = max(epsilon_e / 2.0, 1e-12)
        sigma_q = max(float(np.std(q)), 1e-12)
        score = ((ekin - ekin_target) / sigma_e) ** 2 - 0.1 * (q / sigma_q)
        chosen = int(np.argmin(score))
        failure_mode = "predicted_feasible_but_kwant_failed_E_constraint"

    a = float(rows["a"][chosen])
    ar = float(rows["aspect_ratio"][chosen])
    b = float(rows["b"][chosen])
    e0 = float(rows["E0"][chosen])
    e1 = float(rows["E1"][chosen])
    e2 = float(rows["E2"][chosen])
    e3 = float(rows["E3"][chosen])
    de1 = float(rows["dE1"][chosen])
    ekin_kwant = float(rows["Ekin"][chosen])
    q_kwant = float(rows["Q"][chosen])
    geom = geometry_diagnostics(a=a, b=b, n=n_value)
    passes = abs(ekin_kwant - ekin_target) <= epsilon_e
    return VerifiedRow(
        n=n_value,
        candidate_rank=None,
        candidate_type="best_training_baseline",
        a=a,
        b=b,
        aspect_ratio=ar,
        ekin_target=ekin_target,
        ekin_pred=ekin_kwant,
        de1_pred=de1,
        q_pred=q_kwant,
        e0_kwant=e0,
        e1_kwant=e1,
        e2_kwant=e2,
        e3_kwant=e3,
        ekin_kwant=ekin_kwant,
        de1_kwant=de1,
        q_kwant=q_kwant,
        ekin_error=0.0,
        de1_error=0.0,
        q_error=0.0,
        passes_ekin_constraint_pred=passes,
        passes_ekin_constraint_kwant=passes,
        geometry_hash=geom.geometry_hash,
        n_sites=geom.n_sites,
        n_a=geom.n_a,
        n_b=geom.n_b,
        imbalance_ratio=geom.imbalance_ratio,
        failure_mode=failure_mode,
    )


def random_feasible_candidates(
    n_value: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
    seed: int = 42,
    count: int = 5,
    max_attempts: int = 200,
) -> list[ScreeningCandidate]:
    """Sample random aspect ratios and solve for feasible root candidates."""
    rng = np.random.default_rng(seed)
    out: list[ScreeningCandidate] = []
    seen: set[str] = set()
    attempts = 0
    while len(out) < count and attempts < max_attempts:
        attempts += 1
        ar = float(rng.uniform(MAIN_AR_MIN, MAIN_AR_MAX))
        root, status = find_ekin_root(model_ekin, ar, ekin_target)
        if root is None or status != "ok":
            continue
        cand = make_surrogate_candidate(
            n_value=n_value,
            candidate_type="random_feasible_baseline",
            a=root,
            aspect_ratio=ar,
            ekin_target=ekin_target,
            model_ekin=model_ekin,
            model_de1=model_de1,
        )
        if cand.geometry.geometry_hash in seen:
            continue
        seen.add(cand.geometry.geometry_hash)
        out.append(cand)
    return out


def load_superellipse_dataset(path: str | Path) -> DatasetDict:
    """Load the saved dense superellipse NPZ dataset."""
    loaded = np.load(Path(path))
    return {key: loaded[key] for key in loaded.files}


def load_error_scales(path: str | Path) -> dict[float, dict[str, float]]:
    """Load conservative per-``n`` Ridge error scales from existing reports."""
    scales: dict[float, dict[str, float]] = {}
    report_path = Path(path)
    if not report_path.exists():
        return scales

    import csv

    with report_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n = float(row["n"])
            target = row["target"]
            mae = float(row["ridge_mae"])
            entry = scales.setdefault(n, {"sigma_E": np.nan, "sigma_d": np.nan})
            if target == "E0":
                entry["sigma_E"] = np.nanmax([entry["sigma_E"], mae])
            elif target == "dE1":
                entry["sigma_d"] = np.nanmax([entry["sigma_d"], mae])

    return scales

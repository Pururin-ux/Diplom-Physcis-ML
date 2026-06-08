"""S-objective screening scaffolding under the frozen preregistration protocol.

This module encodes the S-objective rules but does not execute or report the
full experiment by itself. Surrogates are candidate generators only; final
spectral values must come from direct Kwant verification or already
Kwant-computed training rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import spearmanr

from .dataset import DatasetDict, _superellipse_levels_and_site_count
from .geometry import build_superellipse_dot
from .inverse_screening import (
    MAIN_A_MAX,
    MAIN_A_MIN,
    compute_ekin,
    compute_q,
    find_ekin_root,
    physics_feature_matrix,
    site_coordinates_from_system,
    sublattice_counts,
    train_surrogates_for_n,
)
from .symmetry_optimum_analysis import compute_s, train_de2_surrogate_for_n


PREREGISTRATION_COMMIT = "7e28542fda40db288ad2613b49f17b1248f6f2ce"
PROTOCOL_BRANCH = "article-s-objective-preregistration"
IMPLEMENTATION_BRANCH = "article-s-objective-implementation"

PHYSICAL_EFFECT_ONLY_MESSAGE = (
    "physical doublet-splitting effect observed, but no inverse-screening advantage."
)
MONOTONIC_ANISOTROPY_MESSAGE = (
    "S behaves as a monotonic anisotropy diagnostic rather than a non-trivial "
    "inverse-screening objective in this tested domain."
)


@dataclass(frozen=True)
class ProtocolConfig:
    """Frozen constants from the S-objective preregistration."""

    n_values: tuple[float, ...] = (1.2, 2.0, 3.0, 4.0)
    alpha_primary: float = 0.95
    alpha_secondary: float = 0.90
    ekin_tolerance_rel: float = 0.05
    top_k_candidates: int = 5
    jaccard_non_distinct_threshold: float = 0.99
    random_base_seed: int = 20260602
    n_random_repeats: int = 50
    random_aspect_ratio_min: float = 0.67
    random_aspect_ratio_max: float = 1.0
    a_min: float = MAIN_A_MIN
    a_max: float = MAIN_A_MAX
    preregistration_commit: str = PREREGISTRATION_COMMIT
    protocol_branch: str = PROTOCOL_BRANCH
    implementation_branch: str = IMPLEMENTATION_BRANCH
    rules_changed_after_execution: bool = False
    s_experiment_started_after_preregistration: bool = True

    def delta_s_min(self, s_strongest_baseline: float) -> float:
        """Return the frozen dimensionless meaningful-gain threshold."""
        return max(0.02 * float(s_strongest_baseline), 1e-3)

    def report_metadata(self) -> dict[str, object]:
        """Metadata required in future final reports and summary files."""
        return {
            "preregistration_commit": self.preregistration_commit,
            "rules_changed_after_execution": self.rules_changed_after_execution,
            "S_experiment_started_after_preregistration": self.s_experiment_started_after_preregistration,
            "protocol_branch": self.protocol_branch,
            "implementation_branch": self.implementation_branch,
        }


FROZEN_PROTOCOL_VALUES = {
    "n_values": (1.2, 2.0, 3.0, 4.0),
    "alpha_primary": 0.95,
    "alpha_secondary": 0.90,
    "ekin_tolerance_rel": 0.05,
    "top_k_candidates": 5,
    "jaccard_non_distinct_threshold": 0.99,
    "random_base_seed": 20260602,
    "n_random_repeats": 50,
    "random_aspect_ratio_min": 0.67,
    "random_aspect_ratio_max": 1.0,
}


def assert_frozen_protocol_constants(config: ProtocolConfig = ProtocolConfig()) -> None:
    """Assert implementation constants match the preregistered values."""
    for name, expected in FROZEN_PROTOCOL_VALUES.items():
        actual = getattr(config, name)
        if isinstance(expected, tuple):
            if tuple(actual) != expected:
                raise AssertionError(f"{name} changed: expected {expected}, got {actual}.")
        elif isinstance(expected, float):
            if not np.isclose(float(actual), expected, rtol=0.0, atol=1e-12):
                raise AssertionError(f"{name} changed: expected {expected}, got {actual}.")
        elif actual != expected:
            raise AssertionError(f"{name} changed: expected {expected}, got {actual}.")


@dataclass(frozen=True)
class DiscreteGeometry:
    """Realized discrete lattice geometry diagnostics."""

    site_set: tuple[tuple[int, int], ...]
    geometry_hash: str
    n_sites: int
    n_a: int
    n_b: int
    imbalance_ratio: float


@dataclass(frozen=True)
class SCandidate:
    """Surrogate-generated S-objective candidate before direct verification."""

    n: float
    candidate_type: str
    a: float
    b: float
    aspect_ratio: float
    ekin_target: float
    ekin_pred: float
    de1_pred: float
    de2_pred: float
    q_pred: float
    s_pred: float
    geometry: DiscreteGeometry
    candidate_rank: int | None = None
    failure_mode: str = "ok"


@dataclass(frozen=True)
class VerifiedSCandidate:
    """Candidate or baseline with direct Kwant or training-row values."""

    n: float
    candidate_type: str
    a: float
    b: float
    aspect_ratio: float
    ekin_target: float
    e0_kwant: float
    e1_kwant: float
    e2_kwant: float
    e3_kwant: float
    ekin_kwant: float
    de1_kwant: float
    de2_kwant: float
    q_kwant: float
    s_kwant: float
    geometry: DiscreteGeometry
    candidate_rank: int | None = None
    failure_mode: str = "ok"


@dataclass(frozen=True)
class BaselineEvaluation:
    """One feasible or infeasible S-objective baseline."""

    baseline_type: str
    feasible: bool
    s_kwant: float = np.nan
    candidate: VerifiedSCandidate | None = None
    failure_modes: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""
    extras: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StrongestBaselineSelection:
    """Strongest feasible baseline and explicit excluded baseline failures."""

    strongest: BaselineEvaluation | None
    excluded_failure_modes: tuple[str, ...]


@dataclass(frozen=True)
class SingleNPassEvaluation:
    """Frozen pass/fail evaluation for one n and one alpha."""

    n: float
    alpha: float
    passed: bool
    strongest_baseline_type: str | None
    s_candidate: float
    s_strongest_baseline: float
    delta_s_min: float
    failure_modes: tuple[str, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class AlphaAwareProposalDiagnostics:
    """No-output diagnostics for one n/alpha proposal context."""

    n: float
    alpha: float
    ekin_target: float
    q_iso_pred: float
    threshold_q_pred: float
    raw_candidates_generated: int
    predicted_q_feasible_count: int
    selected_method_candidate_count: int
    selected_aspect_ratios: tuple[float, ...]
    selected_s_pred_values: tuple[float, ...]
    selected_q_pred_values: tuple[float, ...]
    failure_mode: str


REPORT_METADATA_COLUMNS = [
    "preregistration_commit",
    "rules_changed_after_execution",
    "S_experiment_started_after_preregistration",
    "protocol_branch",
    "implementation_branch",
]

S_CANDIDATES_VERIFIED_COLUMNS = REPORT_METADATA_COLUMNS + [
    "n",
    "alpha",
    "candidate_rank",
    "candidate_type",
    "a",
    "b",
    "aspect_ratio",
    "Ekin_target",
    "E0_Kwant",
    "E1_Kwant",
    "E2_Kwant",
    "E3_Kwant",
    "Ekin_Kwant",
    "dE1_Kwant",
    "dE2_Kwant",
    "Q_Kwant",
    "S_Kwant",
    "geometry_hash",
    "N_sites",
    "N_A",
    "N_B",
    "imbalance_ratio",
    "failure_mode",
]

BASELINES_BY_N_COLUMNS = REPORT_METADATA_COLUMNS + [
    "n",
    "alpha",
    "baseline_type",
    "feasible",
    "S_Kwant",
    "geometry_hash",
    "failure_modes",
    "notes",
]

RANDOM_BASELINE_REPEATS_COLUMNS = REPORT_METADATA_COLUMNS + [
    "n",
    "alpha",
    "repeat_index",
    "seed",
    "sample_index",
    "aspect_ratio",
    "a",
    "feasible",
    "S_Kwant",
    "failure_mode",
]

SUMMARY_BY_N_COLUMNS = REPORT_METADATA_COLUMNS + [
    "n",
    "alpha",
    "passed",
    "S_candidate_Kwant",
    "S_strongest_baseline",
    "delta_S_min",
    "strongest_baseline_type",
    "failure_modes",
    "notes",
]

FUTURE_OUTPUT_SCHEMAS = {
    "s_candidates_verified.csv": S_CANDIDATES_VERIFIED_COLUMNS,
    "baselines_by_n.csv": BASELINES_BY_N_COLUMNS,
    "random_baseline_repeats.csv": RANDOM_BASELINE_REPEATS_COLUMNS,
    "summary_by_n.csv": SUMMARY_BY_N_COLUMNS,
}


def _as_sorted_site_tuple(site_set: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Normalize a site iterable to sorted integer lattice coordinates."""
    return tuple(sorted((int(x), int(y)) for x, y in site_set))


def geometry_hash_from_sites(site_set: Iterable[tuple[int, int]]) -> str:
    """Hash only the realized discrete Kwant site set."""
    sorted_sites = _as_sorted_site_tuple(site_set)
    return hashlib.sha256(repr(sorted_sites).encode("utf-8")).hexdigest()


def jaccard_site_overlap(
    site_set_a: Iterable[tuple[int, int]],
    site_set_b: Iterable[tuple[int, int]],
) -> float:
    """Return Jaccard overlap between two discrete site sets."""
    set_a = set(_as_sorted_site_tuple(site_set_a))
    set_b = set(_as_sorted_site_tuple(site_set_b))
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def discrete_geometry_from_sites(site_set: Iterable[tuple[int, int]]) -> DiscreteGeometry:
    """Build diagnostics from realized integer lattice sites."""
    coords = _as_sorted_site_tuple(site_set)
    n_a, n_b = sublattice_counts(coords)
    n_sites = len(coords)
    imbalance = abs(n_a - n_b) / n_sites if n_sites else np.nan
    return DiscreteGeometry(
        site_set=coords,
        geometry_hash=geometry_hash_from_sites(coords),
        n_sites=n_sites,
        n_a=n_a,
        n_b=n_b,
        imbalance_ratio=float(imbalance),
    )


def discrete_geometry_for_superellipse(a: float, b: float, n: float) -> DiscreteGeometry:
    """Build a superellipse and hash its realized discrete Kwant site set."""
    fsys = build_superellipse_dot(a=float(a), b=float(b), n=float(n))
    return discrete_geometry_from_sites(site_coordinates_from_system(fsys))


def compute_ekin_targets(training_df: Mapping[str, object], n_values: Sequence[float] | None = None) -> dict[float, float]:
    """Return ``Ekin_target(n) = median(Ekin)`` over all training rows for each n."""
    n_arr = np.asarray(training_df["n"], dtype=float)
    if "Ekin" in training_df:
        ekin_arr = np.asarray(training_df["Ekin"], dtype=float)
    else:
        ekin_arr = np.asarray(compute_ekin(np.asarray(training_df["E0"], dtype=float)), dtype=float)

    target_n_values = tuple(float(n) for n in n_values) if n_values is not None else tuple(sorted(set(n_arr)))
    targets: dict[float, float] = {}
    for n_value in target_n_values:
        mask = np.isclose(n_arr, float(n_value))
        if not np.any(mask):
            raise ValueError(f"No training rows for n={n_value}.")
        targets[float(n_value)] = float(np.median(ekin_arr[mask]))
    return targets


def train_s_surrogates_for_n(dataset: DatasetDict, n_value: float) -> tuple[object, object, object, dict[str, np.ndarray]]:
    """Train Ekin, dE1, and dE2 surrogates for one fixed n."""
    model_ekin, model_de1, rows = train_surrogates_for_n(dataset, n_value)
    model_de2 = train_de2_surrogate_for_n(dataset, n_value)
    return model_ekin, model_de1, model_de2, rows


def solve_candidate_at_aspect_ratio(
    n_value: float,
    aspect_ratio: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
    model_de2: object,
    config: ProtocolConfig = ProtocolConfig(),
    candidate_type: str = "method_candidate",
    candidate_rank: int | None = None,
) -> SCandidate | None:
    """Choose shape via aspect ratio, then determine a from the Ekin root rule."""
    root, status = find_ekin_root(
        model_ekin,
        aspect_ratio=float(aspect_ratio),
        ekin_target=float(ekin_target),
        a_min=config.a_min,
        a_max=config.a_max,
    )
    if root is None or status != "ok":
        return None

    a_value = float(root)
    ar_value = float(aspect_ratio)
    b_value = a_value * ar_value
    x = physics_feature_matrix(np.array([a_value]), np.array([ar_value]))
    ekin_pred = float(model_ekin.predict(x)[0])
    de1_pred = float(model_de1.predict(x)[0])
    de2_pred = float(model_de2.predict(x)[0])
    return SCandidate(
        n=float(n_value),
        candidate_type=candidate_type,
        a=a_value,
        b=b_value,
        aspect_ratio=ar_value,
        ekin_target=float(ekin_target),
        ekin_pred=ekin_pred,
        de1_pred=de1_pred,
        de2_pred=de2_pred,
        q_pred=float(compute_q(de1_pred, ekin_pred)),
        s_pred=float(compute_s(de2_pred, ekin_pred)),
        geometry=discrete_geometry_for_superellipse(a_value, b_value, float(n_value)),
        candidate_rank=candidate_rank,
        failure_mode="ok",
    )


def are_candidates_distinct(
    candidate_a: SCandidate,
    candidate_b: SCandidate,
    config: ProtocolConfig = ProtocolConfig(),
) -> bool:
    """Return whether two candidates count as distinct under the frozen rule."""
    if candidate_a.geometry.geometry_hash == candidate_b.geometry.geometry_hash:
        return False
    overlap = jaccard_site_overlap(candidate_a.geometry.site_set, candidate_b.geometry.site_set)
    return overlap <= config.jaccard_non_distinct_threshold


def select_top_k_diverse_candidates(
    candidates: Sequence[SCandidate],
    config: ProtocolConfig = ProtocolConfig(),
) -> list[SCandidate]:
    """Select up to top-k predicted-S candidates after hash/Jaccard deduplication."""
    assert_frozen_protocol_constants(config)
    selected: list[SCandidate] = []
    for cand in sorted(candidates, key=lambda item: item.s_pred, reverse=True):
        if all(are_candidates_distinct(cand, prev, config) for prev in selected):
            selected.append(cand)
        if len(selected) >= config.top_k_candidates:
            break
    return [
        SCandidate(
            n=c.n,
            candidate_type=c.candidate_type,
            a=c.a,
            b=c.b,
            aspect_ratio=c.aspect_ratio,
            ekin_target=c.ekin_target,
            ekin_pred=c.ekin_pred,
            de1_pred=c.de1_pred,
            de2_pred=c.de2_pred,
            q_pred=c.q_pred,
            s_pred=c.s_pred,
            geometry=c.geometry,
            candidate_rank=i + 1,
            failure_mode=c.failure_mode,
        )
        for i, c in enumerate(selected)
    ]


def select_alpha_aware_top_k_candidates(
    candidates: Sequence[SCandidate],
    q_iso_pred: float,
    alpha: float,
    config: ProtocolConfig = ProtocolConfig(),
) -> tuple[list[SCandidate], float, str]:
    """Select top-k S candidates from the predicted-Q-feasible pool only."""
    assert_frozen_protocol_constants(config)
    threshold_q_pred = float(alpha) * float(q_iso_pred)
    feasible = [cand for cand in candidates if cand.q_pred >= threshold_q_pred]
    selected = select_top_k_diverse_candidates(feasible, config)
    if not feasible:
        return selected, threshold_q_pred, "no_predicted_q_feasible_candidates"
    if len(selected) < config.top_k_candidates:
        return selected, threshold_q_pred, "fewer_than_top_k_predicted_q_feasible_candidates"
    return selected, threshold_q_pred, "ok"


def default_aspect_ratio_grid(config: ProtocolConfig = ProtocolConfig()) -> np.ndarray:
    """Return the established dense aspect-ratio grid for candidate proposals."""
    return np.round(
        np.arange(config.random_aspect_ratio_min, config.random_aspect_ratio_max + 0.0001, 0.005),
        3,
    )


def generate_alpha_aware_method_candidates_for_n(
    dataset: DatasetDict,
    n_value: float,
    config: ProtocolConfig = ProtocolConfig(),
    aspect_ratio_grid: np.ndarray | None = None,
    alpha: float | None = None,
) -> tuple[list[SCandidate], list[dict[str, object]], float, AlphaAwareProposalDiagnostics]:
    """Generate alpha-aware top-5 S candidates with surrogate iso-Ekin roots."""
    assert_frozen_protocol_constants(config)
    alpha_value = config.alpha_primary if alpha is None else float(alpha)
    model_ekin, model_de1, model_de2, rows = train_s_surrogates_for_n(dataset, n_value)
    ekin_target = float(np.median(rows["Ekin"]))
    grid = default_aspect_ratio_grid(config) if aspect_ratio_grid is None else aspect_ratio_grid
    raw_candidates: list[SCandidate] = []
    audit_rows: list[dict[str, object]] = []

    iso_pred = solve_candidate_at_aspect_ratio(
        n_value=n_value,
        aspect_ratio=config.random_aspect_ratio_max,
        ekin_target=ekin_target,
        model_ekin=model_ekin,
        model_de1=model_de1,
        model_de2=model_de2,
        config=config,
        candidate_type="isotropic_same_n_pred_reference",
    )
    if iso_pred is None:
        diagnostics = AlphaAwareProposalDiagnostics(
            n=float(n_value),
            alpha=alpha_value,
            ekin_target=ekin_target,
            q_iso_pred=np.nan,
            threshold_q_pred=np.nan,
            raw_candidates_generated=0,
            predicted_q_feasible_count=0,
            selected_method_candidate_count=0,
            selected_aspect_ratios=(),
            selected_s_pred_values=(),
            selected_q_pred_values=(),
            failure_mode="isotropic_pred_reference_unavailable",
        )
        audit_rows.append(
            {
                "n": n_value,
                "alpha": alpha_value,
                "Ekin_target": ekin_target,
                "failure_mode": diagnostics.failure_mode,
            }
        )
        return [], audit_rows, ekin_target, diagnostics

    q_iso_pred = iso_pred.q_pred

    for ar_value in grid:
        cand = solve_candidate_at_aspect_ratio(
            n_value=n_value,
            aspect_ratio=float(ar_value),
            ekin_target=ekin_target,
            model_ekin=model_ekin,
            model_de1=model_de1,
            model_de2=model_de2,
            config=config,
            candidate_type="method_candidate",
        )
        if cand is None:
            audit_rows.append(
                {
                    "n": n_value,
                    "alpha": alpha_value,
                    "aspect_ratio": float(ar_value),
                    "Q_iso_pred": q_iso_pred,
                    "failure_mode": "no_ekin_root",
                }
            )
            continue
        raw_candidates.append(cand)

    selected, threshold_q_pred, failure_mode = select_alpha_aware_top_k_candidates(
        raw_candidates,
        q_iso_pred=q_iso_pred,
        alpha=alpha_value,
        config=config,
    )
    selected_hashes = {cand.geometry.geometry_hash for cand in selected}
    predicted_q_feasible_count = sum(1 for cand in raw_candidates if cand.q_pred >= threshold_q_pred)

    for cand in raw_candidates:
        predicted_q_feasible = cand.q_pred >= threshold_q_pred
        audit_rows.append(
            {
                "n": n_value,
                "alpha": alpha_value,
                "aspect_ratio": cand.aspect_ratio,
                "a": cand.a,
                "b": cand.b,
                "Ekin_target": ekin_target,
                "S_pred": cand.s_pred,
                "Q_pred": cand.q_pred,
                "Q_iso_pred": q_iso_pred,
                "threshold_q_pred": threshold_q_pred,
                "predicted_q_feasible": predicted_q_feasible,
                "candidate_role": "selected_method_candidate"
                if cand.geometry.geometry_hash in selected_hashes
                else "unconstrained_diagnostic_only",
                "geometry_hash": cand.geometry.geometry_hash,
                "failure_mode": "ok" if predicted_q_feasible else "predicted_q_infeasible",
            }
        )

    diagnostics = AlphaAwareProposalDiagnostics(
        n=float(n_value),
        alpha=alpha_value,
        ekin_target=ekin_target,
        q_iso_pred=float(q_iso_pred),
        threshold_q_pred=float(threshold_q_pred),
        raw_candidates_generated=len(raw_candidates),
        predicted_q_feasible_count=predicted_q_feasible_count,
        selected_method_candidate_count=len(selected),
        selected_aspect_ratios=tuple(cand.aspect_ratio for cand in selected),
        selected_s_pred_values=tuple(cand.s_pred for cand in selected),
        selected_q_pred_values=tuple(cand.q_pred for cand in selected),
        failure_mode=failure_mode,
    )
    return selected, audit_rows, ekin_target, diagnostics


def generate_method_candidates_for_n(
    dataset: DatasetDict,
    n_value: float,
    config: ProtocolConfig = ProtocolConfig(),
    aspect_ratio_grid: np.ndarray | None = None,
    alpha: float | None = None,
) -> tuple[list[SCandidate], list[dict[str, object]], float]:
    """Generate alpha-aware top-5 S candidates and preserve the old return shape."""
    selected, audit_rows, ekin_target, _ = generate_alpha_aware_method_candidates_for_n(
        dataset=dataset,
        n_value=n_value,
        config=config,
        aspect_ratio_grid=aspect_ratio_grid,
        alpha=alpha,
    )
    return selected, audit_rows, ekin_target


def alpha_aware_proposal_diagnostics(
    dataset: DatasetDict,
    config: ProtocolConfig = ProtocolConfig(),
    alphas: Sequence[float] | None = None,
) -> list[AlphaAwareProposalDiagnostics]:
    """Return no-output proposal diagnostics for each n and alpha."""
    alpha_values = (config.alpha_primary, config.alpha_secondary) if alphas is None else tuple(alphas)
    out: list[AlphaAwareProposalDiagnostics] = []
    for n_value in config.n_values:
        for alpha in alpha_values:
            _, _, _, diagnostics = generate_alpha_aware_method_candidates_for_n(
                dataset=dataset,
                n_value=n_value,
                config=config,
                alpha=float(alpha),
            )
            out.append(diagnostics)
    return out


def training_q_by_aspect_ratio_diagnostics(
    dataset: DatasetDict,
    config: ProtocolConfig = ProtocolConfig(),
) -> list[dict[str, object]]:
    """Summarize already Kwant-computed training Q values by n and aspect ratio."""
    n_arr = np.asarray(dataset["n"], dtype=float)
    ar_arr = np.asarray(dataset["aspect_ratio"], dtype=float)
    e0_arr = np.asarray(dataset["E0"], dtype=float)
    de1_arr = np.asarray(dataset["dE1"], dtype=float)
    q_arr = np.asarray(compute_q(de1_arr, compute_ekin(e0_arr)), dtype=float)
    out: list[dict[str, object]] = []
    for n_value in config.n_values:
        n_mask = np.isclose(n_arr, float(n_value))
        if not np.any(n_mask):
            continue
        rho = float(spearmanr(ar_arr[n_mask], q_arr[n_mask]).statistic)
        trend = "Q increases with aspect_ratio; Q tends to decrease as aspect_ratio decreases" if rho > 0 else (
            "Q decreases with aspect_ratio" if rho < 0 else "no monotonic rank trend"
        )
        for ar_value in sorted(set(float(value) for value in ar_arr[n_mask])):
            mask = n_mask & np.isclose(ar_arr, ar_value)
            q_values = q_arr[mask]
            out.append(
                {
                    "n": float(n_value),
                    "aspect_ratio": float(ar_value),
                    "n_rows": int(q_values.size),
                    "Q_mean": float(np.mean(q_values)),
                    "Q_min": float(np.min(q_values)),
                    "Q_max": float(np.max(q_values)),
                    "spearman_r_ar_Q_for_n": rho,
                    "interpretation": trend,
                }
            )
    return out


def random_seeds(config: ProtocolConfig = ProtocolConfig()) -> list[int]:
    """Return frozen deterministic random-baseline seeds."""
    assert_frozen_protocol_constants(config)
    return [config.random_base_seed + i for i in range(config.n_random_repeats)]


def random_aspect_ratio_draws(seed: int, config: ProtocolConfig = ProtocolConfig(), count: int | None = None) -> np.ndarray:
    """Sample random baseline shapes; a is intentionally not sampled here."""
    assert_frozen_protocol_constants(config)
    n_draws = config.top_k_candidates if count is None else int(count)
    rng = np.random.default_rng(int(seed))
    return rng.uniform(config.random_aspect_ratio_min, config.random_aspect_ratio_max, size=n_draws)


CandidateFactory = Callable[
    [float, float, float, object, object, object, ProtocolConfig, str, int | None],
    SCandidate | None,
]


def random_baseline_candidates_for_repeat(
    n_value: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
    model_de2: object,
    seed: int,
    config: ProtocolConfig = ProtocolConfig(),
    candidate_factory: CandidateFactory = solve_candidate_at_aspect_ratio,
) -> list[SCandidate]:
    """Construct random baseline candidates by sampling aspect_ratio only."""
    candidates: list[SCandidate] = []
    for idx, ar_value in enumerate(random_aspect_ratio_draws(seed, config)):
        cand = candidate_factory(
            float(n_value),
            float(ar_value),
            float(ekin_target),
            model_ekin,
            model_de1,
            model_de2,
            config,
            "random_best_of_5_member",
            idx + 1,
        )
        if cand is not None:
            candidates.append(cand)
    return candidates


def verify_candidate_kwant(candidate: SCandidate) -> VerifiedSCandidate:
    """Direct-Kwant verify a candidate and compute S/Q diagnostics."""
    vals, _ = _superellipse_levels_and_site_count(a=candidate.a, b=candidate.b, n=candidate.n)
    e0, e1, e2, e3 = [float(v) for v in vals]
    ekin = float(compute_ekin(e0))
    de1 = e1 - e0
    de2 = e2 - e1
    geometry = discrete_geometry_for_superellipse(candidate.a, candidate.b, candidate.n)
    return VerifiedSCandidate(
        n=candidate.n,
        candidate_type=candidate.candidate_type,
        a=candidate.a,
        b=candidate.b,
        aspect_ratio=candidate.aspect_ratio,
        ekin_target=candidate.ekin_target,
        e0_kwant=e0,
        e1_kwant=e1,
        e2_kwant=e2,
        e3_kwant=e3,
        ekin_kwant=ekin,
        de1_kwant=de1,
        de2_kwant=de2,
        q_kwant=float(compute_q(de1, ekin)),
        s_kwant=float(compute_s(de2, ekin)),
        geometry=geometry,
        candidate_rank=candidate.candidate_rank,
        failure_mode="ok",
    )


def is_ekin_feasible(
    candidate: VerifiedSCandidate,
    ekin_target: float | None = None,
    config: ProtocolConfig = ProtocolConfig(),
) -> bool:
    """Return whether a verified row satisfies frozen relative Ekin tolerance."""
    target = candidate.ekin_target if ekin_target is None else float(ekin_target)
    if target <= 0.0 or not np.isfinite(candidate.ekin_kwant):
        return False
    return abs(candidate.ekin_kwant - target) / target <= config.ekin_tolerance_rel


def is_q_feasible(candidate: VerifiedSCandidate, q_iso: float, alpha: float) -> bool:
    """Return whether a verified row preserves Q at the requested alpha."""
    return bool(np.isfinite(candidate.q_kwant) and candidate.q_kwant >= float(alpha) * float(q_iso))


def verified_training_rows_for_n(dataset: DatasetDict, n_value: float) -> list[VerifiedSCandidate]:
    """Convert already Kwant-computed training rows to verified S rows."""
    n_arr = np.asarray(dataset["n"], dtype=float)
    mask = np.isclose(n_arr, float(n_value))
    out: list[VerifiedSCandidate] = []
    for idx in np.flatnonzero(mask):
        a = float(dataset["a"][idx])
        b = float(dataset["b"][idx])
        ar = float(dataset["aspect_ratio"][idx])
        e0 = float(dataset["E0"][idx])
        e1 = float(dataset["E1"][idx])
        e2 = float(dataset["E2"][idx])
        e3 = float(dataset["E3"][idx])
        ekin = float(compute_ekin(e0))
        de1 = e1 - e0
        de2 = e2 - e1
        out.append(
            VerifiedSCandidate(
                n=float(n_value),
                candidate_type="training_row",
                a=a,
                b=b,
                aspect_ratio=ar,
                ekin_target=np.nan,
                e0_kwant=e0,
                e1_kwant=e1,
                e2_kwant=e2,
                e3_kwant=e3,
                ekin_kwant=ekin,
                de1_kwant=de1,
                de2_kwant=de2,
                q_kwant=float(compute_q(de1, ekin)),
                s_kwant=float(compute_s(de2, ekin)),
                geometry=discrete_geometry_for_superellipse(a, b, float(n_value)),
                failure_mode="ok",
            )
        )
    return out


def best_training_baseline_under_constraints(
    training_rows: Sequence[VerifiedSCandidate],
    ekin_target: float,
    q_iso: float,
    alpha: float,
    config: ProtocolConfig = ProtocolConfig(),
) -> BaselineEvaluation:
    """Select best already Kwant-computed training row under Ekin/Q constraints."""
    feasible = [
        row
        for row in training_rows
        if is_ekin_feasible(row, ekin_target, config) and is_q_feasible(row, q_iso, alpha)
    ]
    if not feasible:
        return BaselineEvaluation(
            baseline_type="best_training",
            feasible=False,
            failure_modes=("best_training_infeasible",),
            notes="No training row satisfied the same Ekin/Q constraints.",
        )
    best = max(feasible, key=lambda row: row.s_kwant)
    return BaselineEvaluation(
        baseline_type="best_training",
        feasible=True,
        s_kwant=best.s_kwant,
        candidate=best,
    )


def isotropic_same_n_reference(
    n_value: float,
    ekin_target: float,
    model_ekin: object,
    model_de1: object,
    model_de2: object,
    config: ProtocolConfig = ProtocolConfig(),
) -> BaselineEvaluation:
    """Build and verify the isotropic same-n physical-effect reference."""
    cand = solve_candidate_at_aspect_ratio(
        n_value=n_value,
        aspect_ratio=config.random_aspect_ratio_max,
        ekin_target=ekin_target,
        model_ekin=model_ekin,
        model_de1=model_de1,
        model_de2=model_de2,
        config=config,
        candidate_type="isotropic_same_n_reference",
    )
    if cand is None:
        return BaselineEvaluation(
            baseline_type="isotropic_same_n",
            feasible=False,
            failure_modes=("isotropic_same_n_no_ekin_root",),
        )
    verified = verify_candidate_kwant(cand)
    if not is_ekin_feasible(verified, ekin_target, config):
        return BaselineEvaluation(
            baseline_type="isotropic_same_n",
            feasible=False,
            candidate=verified,
            failure_modes=("isotropic_same_n_ekin_infeasible",),
        )
    return BaselineEvaluation(
        baseline_type="isotropic_same_n",
        feasible=True,
        s_kwant=verified.s_kwant,
        candidate=verified,
    )


def simple_anisotropy_heuristic_baseline(
    verified_rows: Sequence[VerifiedSCandidate],
    ekin_target: float,
    q_iso: float,
    alpha: float,
    config: ProtocolConfig = ProtocolConfig(),
) -> BaselineEvaluation:
    """Select the smallest feasible aspect_ratio under the same Ekin/Q constraints."""
    feasible = [
        row
        for row in verified_rows
        if is_ekin_feasible(row, ekin_target, config) and is_q_feasible(row, q_iso, alpha)
    ]
    if not feasible:
        return BaselineEvaluation(
            baseline_type="simple_anisotropy_heuristic",
            feasible=False,
            failure_modes=("simple_anisotropy_heuristic_infeasible",),
            notes="No candidate satisfied Ekin/Q constraints for the heuristic.",
        )
    chosen = min(feasible, key=lambda row: (row.aspect_ratio, -row.s_kwant))
    return BaselineEvaluation(
        baseline_type="simple_anisotropy_heuristic",
        feasible=True,
        s_kwant=chosen.s_kwant,
        candidate=chosen,
    )


def random_best_of_5_baseline_from_repeats(
    repeat_candidates: Mapping[int, Sequence[VerifiedSCandidate]],
    ekin_target: float,
    q_iso: float,
    alpha: float,
    config: ProtocolConfig = ProtocolConfig(),
) -> BaselineEvaluation:
    """Summarize 50 random best-of-5 repeats using median as primary baseline."""
    best_s_values: list[float] = []
    for rows in repeat_candidates.values():
        feasible = [
            row
            for row in rows
            if is_ekin_feasible(row, ekin_target, config) and is_q_feasible(row, q_iso, alpha)
        ]
        if feasible:
            best_s_values.append(max(row.s_kwant for row in feasible))
    if not best_s_values:
        return BaselineEvaluation(
            baseline_type="random_best_of_5_primary",
            feasible=False,
            failure_modes=("random_baseline_infeasible",),
            notes="No random repeat produced feasible candidates.",
            extras={"n_feasible_repeats": 0},
        )
    values = np.asarray(best_s_values, dtype=float)
    return BaselineEvaluation(
        baseline_type="random_best_of_5_primary",
        feasible=True,
        s_kwant=float(np.median(values)),
        failure_modes=(),
        extras={
            "S_random_best_of_5_primary": float(np.median(values)),
            "S_random_best_of_5_p75": float(np.percentile(values, 75)),
            "n_feasible_repeats": len(best_s_values),
        },
    )


def select_strongest_feasible_baseline(
    baselines: Sequence[BaselineEvaluation],
) -> StrongestBaselineSelection:
    """Select max-S feasible baseline and retain explicit exclusion notes."""
    feasible = [baseline for baseline in baselines if baseline.feasible and np.isfinite(baseline.s_kwant)]
    excluded: list[str] = []
    for baseline in baselines:
        if not baseline.feasible:
            excluded.extend(baseline.failure_modes or (f"{baseline.baseline_type}_infeasible",))
    strongest = max(feasible, key=lambda baseline: baseline.s_kwant) if feasible else None
    return StrongestBaselineSelection(strongest=strongest, excluded_failure_modes=tuple(excluded))


def _baseline_by_type(
    baselines: Sequence[BaselineEvaluation],
    baseline_type: str,
) -> BaselineEvaluation | None:
    for baseline in baselines:
        if baseline.baseline_type == baseline_type:
            return baseline
    return None


def evaluate_single_n_pass(
    candidate: VerifiedSCandidate,
    baselines: Sequence[BaselineEvaluation],
    alpha: float,
    config: ProtocolConfig = ProtocolConfig(),
    q_iso: float | None = None,
) -> SingleNPassEvaluation:
    """Apply the frozen single-n pass/fail rule."""
    assert_frozen_protocol_constants(config)
    iso = _baseline_by_type(baselines, "isotropic_same_n")
    simple = _baseline_by_type(baselines, "simple_anisotropy_heuristic")
    if q_iso is None:
        if iso is None or iso.candidate is None:
            raise ValueError("Need q_iso or a feasible isotropic baseline candidate.")
        q_iso_value = iso.candidate.q_kwant
    else:
        q_iso_value = float(q_iso)

    selection = select_strongest_feasible_baseline(baselines)
    failure_modes: list[str] = []
    notes: list[str] = []
    notes.extend(f"excluded_infeasible_baseline:{mode}" for mode in selection.excluded_failure_modes)
    strongest = selection.strongest
    if strongest is None:
        failure_modes.append("no_feasible_baseline")
        return SingleNPassEvaluation(
            n=candidate.n,
            alpha=float(alpha),
            passed=False,
            strongest_baseline_type=None,
            s_candidate=candidate.s_kwant,
            s_strongest_baseline=np.nan,
            delta_s_min=np.nan,
            failure_modes=tuple(failure_modes),
            notes=tuple(notes),
        )

    delta = config.delta_s_min(strongest.s_kwant)
    if not is_ekin_feasible(candidate, candidate.ekin_target, config):
        failure_modes.append("candidate_ekin_tolerance_failed")
    if not is_q_feasible(candidate, q_iso_value, alpha):
        failure_modes.append("candidate_q_preservation_failed")
    if not candidate.s_kwant > strongest.s_kwant + delta:
        failure_modes.append("candidate_does_not_beat_strongest_feasible_baseline")
        if iso is not None and iso.feasible and candidate.s_kwant > iso.s_kwant:
            notes.append(PHYSICAL_EFFECT_ONLY_MESSAGE)

    if strongest.candidate is not None and candidate.geometry.geometry_hash == strongest.candidate.geometry.geometry_hash:
        failure_modes.append("candidate_duplicate_geometry_of_winning_baseline")

    if simple is None or not simple.feasible:
        failure_modes.append("simple_anisotropy_heuristic_infeasible")
    elif not candidate.s_kwant > simple.s_kwant + delta:
        failure_modes.append("candidate_does_not_beat_simple_anisotropy_heuristic")
        notes.append(MONOTONIC_ANISOTROPY_MESSAGE)
        if (
            simple.candidate is not None
            and candidate.aspect_ratio <= simple.candidate.aspect_ratio + 1e-12
        ):
            failure_modes.append("result_collapses_to_monotonic_anisotropy_heuristic")

    return SingleNPassEvaluation(
        n=candidate.n,
        alpha=float(alpha),
        passed=not failure_modes,
        strongest_baseline_type=strongest.baseline_type,
        s_candidate=candidate.s_kwant,
        s_strongest_baseline=strongest.s_kwant,
        delta_s_min=delta,
        failure_modes=tuple(failure_modes),
        notes=tuple(dict.fromkeys(notes)),
    )


def summarize_across_n(
    results: Sequence[SingleNPassEvaluation],
    config: ProtocolConfig = ProtocolConfig(),
) -> dict[str, object]:
    """Classify across-n support using alpha=0.95 as primary."""
    primary = [row for row in results if np.isclose(row.alpha, config.alpha_primary)]
    passed = sum(1 for row in primary if row.passed)
    if passed == 4:
        level = "primary success"
    elif passed == 3:
        level = "partial support"
    elif passed in (1, 2):
        level = "exploratory / shape-dependent"
    else:
        level = "negative result"
    return {
        "alpha_primary": config.alpha_primary,
        "primary_n_evaluated": len(primary),
        "primary_n_passed": passed,
        "support_level": level,
        "secondary_alpha_note": "alpha=0.90 is secondary and cannot override alpha=0.95 failure",
    }


def add_report_metadata(row: Mapping[str, object], config: ProtocolConfig = ProtocolConfig()) -> dict[str, object]:
    """Attach required preregistration metadata to one future report row."""
    return {**config.report_metadata(), **dict(row)}

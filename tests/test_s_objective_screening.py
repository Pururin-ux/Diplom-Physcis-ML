"""Tests for S-objective preregistered screening scaffolding."""

from __future__ import annotations

import numpy as np
import pytest

from src import s_objective_screening as sobj


def _geom(coords, label: str | None = None) -> sobj.DiscreteGeometry:
    site_set = tuple(sorted((int(x), int(y)) for x, y in coords))
    return sobj.DiscreteGeometry(
        site_set=site_set,
        geometry_hash=label or sobj.geometry_hash_from_sites(site_set),
        n_sites=len(site_set),
        n_a=len(site_set),
        n_b=0,
        imbalance_ratio=1.0 if site_set else np.nan,
    )


def _candidate(
    s_pred: float,
    coords,
    h: str | None = None,
    ar: float = 0.8,
) -> sobj.SCandidate:
    geom = _geom(coords, h)
    return sobj.SCandidate(
        n=2.0,
        candidate_type="method_candidate",
        a=30.0,
        b=30.0 * ar,
        aspect_ratio=ar,
        ekin_target=1.0,
        ekin_pred=1.0,
        de1_pred=1.0,
        de2_pred=s_pred,
        q_pred=1.0,
        s_pred=s_pred,
        geometry=geom,
    )


def _verified(
    s: float,
    q: float = 1.0,
    ekin: float = 1.0,
    target: float = 1.0,
    ar: float = 0.8,
    coords=((0, 0),),
    candidate_type: str = "row",
) -> sobj.VerifiedSCandidate:
    geom = _geom(coords)
    e0 = ekin - 4.0
    de1 = q * ekin
    de2 = s * ekin
    return sobj.VerifiedSCandidate(
        n=2.0,
        candidate_type=candidate_type,
        a=30.0,
        b=30.0 * ar,
        aspect_ratio=ar,
        ekin_target=target,
        e0_kwant=e0,
        e1_kwant=e0 + de1,
        e2_kwant=e0 + de1 + de2,
        e3_kwant=e0 + de1 + de2 + 0.1,
        ekin_kwant=ekin,
        de1_kwant=de1,
        de2_kwant=de2,
        q_kwant=q,
        s_kwant=s,
        geometry=geom,
        failure_mode="ok",
    )


def _baseline(name: str, row: sobj.VerifiedSCandidate | None, feasible: bool = True) -> sobj.BaselineEvaluation:
    if row is None:
        return sobj.BaselineEvaluation(
            baseline_type=name,
            feasible=False,
            failure_modes=(f"{name}_infeasible",),
        )
    return sobj.BaselineEvaluation(
        baseline_type=name,
        feasible=feasible,
        s_kwant=row.s_kwant,
        candidate=row,
        failure_modes=() if feasible else (f"{name}_infeasible",),
    )


def test_protocol_config_matches_frozen_values() -> None:
    """Frozen protocol constants should assert exactly."""
    config = sobj.ProtocolConfig()

    sobj.assert_frozen_protocol_constants(config)

    with pytest.raises(AssertionError):
        sobj.assert_frozen_protocol_constants(sobj.ProtocolConfig(alpha_primary=0.94))


def test_compute_ekin_targets_median_over_fixed_n_rows() -> None:
    """Ekin targets should be median(Ekin) for each fixed n."""
    data = {
        "n": np.array([1.2, 1.2, 2.0, 2.0, 2.0]),
        "E0": np.array([-3.99, -3.97, -3.95, -3.93, -3.91]),
    }

    targets = sobj.compute_ekin_targets(data, n_values=(1.2, 2.0))

    assert np.isclose(targets[1.2], 0.02)
    assert np.isclose(targets[2.0], 0.07)


def test_geometry_hash_stable_and_site_based() -> None:
    """Geometry hash should depend on sorted integer sites, not input order."""
    sites_a = [(1, 0), (0, 0), (0, 1)]
    sites_b = [(0, 1), (1, 0), (0, 0)]

    assert sobj.geometry_hash_from_sites(sites_a) == sobj.geometry_hash_from_sites(sites_b)
    assert sobj.geometry_hash_from_sites(sites_a) != sobj.geometry_hash_from_sites([(0, 0), (1, 0)])


def test_same_site_set_from_different_float_parameters_has_same_hash() -> None:
    """If realized sites are identical, hash must be identical regardless of parameters."""
    realized_sites = [(0, 0), (1, 0), (0, 1)]
    hash_from_params_a = sobj.geometry_hash_from_sites(realized_sites)
    hash_from_params_b = sobj.geometry_hash_from_sites(list(reversed(realized_sites)))

    assert hash_from_params_a == hash_from_params_b


def test_jaccard_site_overlap_logic() -> None:
    """Jaccard overlap should distinguish exact, partial, and empty sets."""
    assert sobj.jaccard_site_overlap([(0, 0)], [(0, 0)]) == 1.0
    assert np.isclose(sobj.jaccard_site_overlap([(0, 0), (1, 0)], [(1, 0), (2, 0)]), 1.0 / 3.0)
    assert sobj.jaccard_site_overlap([], [(1, 0)]) == 0.0
    assert sobj.jaccard_site_overlap([], []) == 1.0


def test_ekin_and_q_feasibility() -> None:
    """Feasibility rules should use frozen relative Ekin tolerance and alpha Q."""
    good = _verified(s=0.1, q=0.96, ekin=1.04, target=1.0)
    bad_e = _verified(s=0.1, q=0.96, ekin=1.06, target=1.0)
    bad_q = _verified(s=0.1, q=0.94, ekin=1.0, target=1.0)

    assert sobj.is_ekin_feasible(good)
    assert not sobj.is_ekin_feasible(bad_e)
    assert sobj.is_q_feasible(good, q_iso=1.0, alpha=0.95)
    assert not sobj.is_q_feasible(bad_q, q_iso=1.0, alpha=0.95)


def test_delta_s_min_computation() -> None:
    """The meaningful S gain threshold should be fixed and dimensionless."""
    config = sobj.ProtocolConfig()

    assert np.isclose(config.delta_s_min(0.01), 1e-3)
    assert np.isclose(config.delta_s_min(0.1), 0.002)
    assert np.isclose(config.delta_s_min(1.0), 0.02)


def test_strongest_feasible_baseline_excludes_infeasible_with_reporting() -> None:
    """Strongest baseline should use only feasible baselines and report exclusions."""
    baselines = [
        _baseline("isotropic_same_n", _verified(s=0.01)),
        _baseline("best_training", None, feasible=False),
        _baseline("simple_anisotropy_heuristic", _verified(s=0.4)),
    ]

    selected = sobj.select_strongest_feasible_baseline(baselines)

    assert selected.strongest is not None
    assert selected.strongest.baseline_type == "simple_anisotropy_heuristic"
    assert "best_training_infeasible" in selected.excluded_failure_modes


def test_single_n_pass_requires_strongest_and_simple_heuristic_gain() -> None:
    """A candidate passes only when it beats the strongest feasible baseline."""
    candidate = _verified(s=0.31, q=0.96, coords=((9, 9),), candidate_type="method_candidate")
    baselines = [
        _baseline("isotropic_same_n", _verified(s=0.01, q=1.0, coords=((0, 0),))),
        _baseline("best_training", _verified(s=0.2, coords=((1, 0),))),
        _baseline("random_best_of_5_primary", _verified(s=0.25, coords=((2, 0),))),
        _baseline("simple_anisotropy_heuristic", _verified(s=0.3, coords=((3, 0),), ar=0.67)),
    ]

    result = sobj.evaluate_single_n_pass(candidate, baselines, alpha=0.95, q_iso=1.0)

    assert result.passed
    assert result.strongest_baseline_type == "simple_anisotropy_heuristic"


def test_single_n_fail_when_candidate_beats_isotropic_only() -> None:
    """Beating isotropic alone should not count as inverse-screening success."""
    candidate = _verified(s=0.05, q=0.96, coords=((9, 9),), candidate_type="method_candidate")
    baselines = [
        _baseline("isotropic_same_n", _verified(s=0.01, q=1.0, coords=((0, 0),))),
        _baseline("best_training", _verified(s=0.15, coords=((1, 0),))),
        _baseline("random_best_of_5_primary", _verified(s=0.2, coords=((2, 0),))),
        _baseline("simple_anisotropy_heuristic", _verified(s=0.3, coords=((3, 0),), ar=0.67)),
    ]

    result = sobj.evaluate_single_n_pass(candidate, baselines, alpha=0.95, q_iso=1.0)

    assert not result.passed
    assert "candidate_does_not_beat_strongest_feasible_baseline" in result.failure_modes
    assert sobj.PHYSICAL_EFFECT_ONLY_MESSAGE in result.notes
    assert sobj.MONOTONIC_ANISOTROPY_MESSAGE in result.notes


def test_single_n_fail_when_duplicate_of_winning_baseline() -> None:
    """Duplicate discrete geometry of the winning baseline should fail."""
    shared = ((5, 5),)
    candidate = _verified(s=0.5, q=0.96, coords=shared, candidate_type="method_candidate")
    baselines = [
        _baseline("isotropic_same_n", _verified(s=0.01, q=1.0, coords=((0, 0),))),
        _baseline("simple_anisotropy_heuristic", _verified(s=0.3, coords=shared, ar=0.67)),
    ]

    result = sobj.evaluate_single_n_pass(candidate, baselines, alpha=0.95, q_iso=1.0)

    assert not result.passed
    assert "candidate_duplicate_geometry_of_winning_baseline" in result.failure_modes


def test_across_n_summary_classification() -> None:
    """Across-n summary should use alpha=0.95 and ignore secondary override."""
    rows = [
        sobj.SingleNPassEvaluation(n=1.2, alpha=0.95, passed=True, strongest_baseline_type="x", s_candidate=1, s_strongest_baseline=0, delta_s_min=0.1, failure_modes=(), notes=()),
        sobj.SingleNPassEvaluation(n=2.0, alpha=0.95, passed=True, strongest_baseline_type="x", s_candidate=1, s_strongest_baseline=0, delta_s_min=0.1, failure_modes=(), notes=()),
        sobj.SingleNPassEvaluation(n=3.0, alpha=0.95, passed=True, strongest_baseline_type="x", s_candidate=1, s_strongest_baseline=0, delta_s_min=0.1, failure_modes=(), notes=()),
        sobj.SingleNPassEvaluation(n=4.0, alpha=0.95, passed=False, strongest_baseline_type="x", s_candidate=1, s_strongest_baseline=0, delta_s_min=0.1, failure_modes=("fail",), notes=()),
        sobj.SingleNPassEvaluation(n=4.0, alpha=0.90, passed=True, strongest_baseline_type="x", s_candidate=1, s_strongest_baseline=0, delta_s_min=0.1, failure_modes=(), notes=()),
    ]

    summary = sobj.summarize_across_n(rows)

    assert summary["primary_n_passed"] == 3
    assert summary["support_level"] == "partial support"
    assert "cannot override" in str(summary["secondary_alpha_note"])


def test_random_seeds_generation() -> None:
    """Random seeds should be frozen deterministic sequence."""
    seeds = sobj.random_seeds()

    assert len(seeds) == 50
    assert seeds[:3] == [20260602, 20260603, 20260604]
    assert seeds[-1] == 20260651


def test_random_baseline_samples_aspect_ratio_only_and_uses_factory_root() -> None:
    """Random baseline should not independently sample a."""
    calls: list[float] = []

    def fake_factory(n, aspect_ratio, ekin_target, model_ekin, model_de1, model_de2, config, candidate_type, rank):
        calls.append(aspect_ratio)
        return _candidate(s_pred=aspect_ratio, coords=((rank, 0),), ar=aspect_ratio)

    candidates = sobj.random_baseline_candidates_for_repeat(
        n_value=2.0,
        ekin_target=1.0,
        model_ekin=object(),
        model_de1=object(),
        model_de2=object(),
        seed=20260602,
        candidate_factory=fake_factory,
    )

    assert len(candidates) == 5
    assert len(calls) == 5
    assert all(0.67 <= ar <= 1.0 for ar in calls)
    assert [cand.aspect_ratio for cand in candidates] == calls


def test_top_5_candidate_budget_and_deduplication() -> None:
    """Top-k selection should deduplicate by hash/Jaccard and cap at five."""
    candidates = [
        _candidate(10.0, [(0, 0), (1, 0)], h="dup"),
        _candidate(9.0, [(0, 0), (1, 0)], h="dup"),
        _candidate(8.0, [(0, 0), (1, 0), (2, 0)], h="near"),
        _candidate(7.0, [(10, 0)], h="a"),
        _candidate(6.0, [(20, 0)], h="b"),
        _candidate(5.0, [(30, 0)], h="c"),
        _candidate(4.0, [(40, 0)], h="d"),
        _candidate(3.0, [(50, 0)], h="e"),
    ]

    selected = sobj.select_top_k_diverse_candidates(candidates)

    assert len(selected) == 5
    assert [cand.s_pred for cand in selected] == [10.0, 8.0, 7.0, 6.0, 5.0]
    assert [cand.candidate_rank for cand in selected] == [1, 2, 3, 4, 5]


def test_random_best_of_5_summary_uses_median_and_p75() -> None:
    """Random baseline summary should use median as primary and report p75."""
    repeats = {
        0: [_verified(s=0.1), _verified(s=0.2)],
        1: [_verified(s=0.3)],
        2: [_verified(s=0.5), _verified(s=0.4)],
    }

    baseline = sobj.random_best_of_5_baseline_from_repeats(repeats, ekin_target=1.0, q_iso=1.0, alpha=0.95)

    assert baseline.feasible
    assert np.isclose(baseline.s_kwant, 0.3)
    assert np.isclose(float(baseline.extras["S_random_best_of_5_p75"]), 0.4)


def test_future_report_metadata_in_schema_and_rows() -> None:
    """Future final report rows should carry preregistration metadata."""
    row = sobj.add_report_metadata({"n": 2.0, "passed": False})

    assert row["preregistration_commit"] == sobj.PREREGISTRATION_COMMIT
    assert row["rules_changed_after_execution"] is False
    assert row["S_experiment_started_after_preregistration"] is True
    assert row["protocol_branch"] == "article-s-objective-preregistration"
    assert row["implementation_branch"] == "article-s-objective-implementation"
    assert "preregistration_commit" in sobj.SUMMARY_BY_N_COLUMNS

"""Runner for S-objective diagnostics and frozen-protocol execution.

Dry-run and capped smoke modes do not write final scientific outputs. The full
S-objective outputs are written only when ``--run-final`` is provided.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from pathlib import Path
import sys
import time

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.s_objective_screening import (  # noqa: E402
    BASELINES_BY_N_COLUMNS,
    FUTURE_OUTPUT_SCHEMAS,
    RANDOM_BASELINE_REPEATS_COLUMNS,
    S_CANDIDATES_VERIFIED_COLUMNS,
    SUMMARY_BY_N_COLUMNS,
    SCandidate,
    SingleNPassEvaluation,
    VerifiedSCandidate,
    ProtocolConfig,
    alpha_aware_proposal_diagnostics,
    add_report_metadata,
    assert_frozen_protocol_constants,
    best_training_baseline_under_constraints,
    default_aspect_ratio_grid,
    compute_ekin_targets,
    evaluate_single_n_pass,
    generate_method_candidates_for_n,
    is_ekin_feasible,
    is_q_feasible,
    isotropic_same_n_reference,
    random_aspect_ratio_draws,
    random_best_of_5_baseline_from_repeats,
    select_alpha_aware_top_k_candidates,
    select_strongest_feasible_baseline,
    simple_anisotropy_heuristic_baseline,
    solve_candidate_at_aspect_ratio,
    summarize_across_n,
    training_q_by_aspect_ratio_diagnostics,
    train_s_surrogates_for_n,
    verify_candidate_kwant,
    verified_training_rows_for_n,
)
from src.inverse_screening import load_superellipse_dataset  # noqa: E402


DATA_PATH = PROJECT_ROOT / "data" / "superellipse_discrete_n_dense_dataset.npz"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_s_objective"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate config and candidate planning only.")
    parser.add_argument(
        "--max-kwant-per-n",
        type=int,
        default=0,
        help="Optional capped direct-Kwant smoke verification count per n; 0 disables Kwant.",
    )
    parser.add_argument(
        "--no-write-final-results",
        action="store_true",
        default=True,
        help="Kept for protocol safety; final result writing is disabled in this implementation commit.",
    )
    parser.add_argument(
        "--write-implementation-audit",
        action="store_true",
        help="Rewrite reports/article_s_objective/implementation_audit.md with current scaffold status.",
    )
    parser.add_argument(
        "--proposal-diagnostics",
        action="store_true",
        help="Print alpha-aware proposal diagnostics without writing final outputs.",
    )
    parser.add_argument(
        "--training-q-diagnostics",
        action="store_true",
        help="Print training-data Q(aspect_ratio) diagnostics without new Kwant computation.",
    )
    parser.add_argument(
        "--run-final",
        action="store_true",
        help="Run the full preregistered S-objective execution and write final outputs.",
    )
    return parser


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _verified_with_cache(
    candidate: SCandidate,
    cache: dict[str, VerifiedSCandidate],
) -> VerifiedSCandidate:
    key = candidate.geometry.geometry_hash
    if key not in cache:
        cache[key] = verify_candidate_kwant(candidate)
        return cache[key]
    base = cache[key]
    return replace(
        base,
        n=candidate.n,
        candidate_type=candidate.candidate_type,
        a=candidate.a,
        b=candidate.b,
        aspect_ratio=candidate.aspect_ratio,
        ekin_target=candidate.ekin_target,
        candidate_rank=candidate.candidate_rank,
        failure_mode=candidate.failure_mode,
    )


def _candidate_row(
    row: VerifiedSCandidate,
    alpha: float,
    q_iso: float,
    config: ProtocolConfig,
    role: str = "method_candidate",
) -> dict[str, object]:
    ekin_feasible = is_ekin_feasible(row, row.ekin_target, config)
    q_feasible = is_q_feasible(row, q_iso, alpha)
    failure_mode = row.failure_mode
    if not ekin_feasible:
        failure_mode = "ekin_tolerance_failed"
    elif not q_feasible:
        failure_mode = "q_preservation_failed"
    return add_report_metadata(
        {
            "n": row.n,
            "alpha": alpha,
            "candidate_rank": "" if row.candidate_rank is None else row.candidate_rank,
            "candidate_type": role,
            "a": row.a,
            "b": row.b,
            "aspect_ratio": row.aspect_ratio,
            "Ekin_target": row.ekin_target,
            "E0_Kwant": row.e0_kwant,
            "E1_Kwant": row.e1_kwant,
            "E2_Kwant": row.e2_kwant,
            "E3_Kwant": row.e3_kwant,
            "Ekin_Kwant": row.ekin_kwant,
            "dE1_Kwant": row.de1_kwant,
            "dE2_Kwant": row.de2_kwant,
            "Q_Kwant": row.q_kwant,
            "S_Kwant": row.s_kwant,
            "geometry_hash": row.geometry.geometry_hash,
            "N_sites": row.geometry.n_sites,
            "N_A": row.geometry.n_a,
            "N_B": row.geometry.n_b,
            "imbalance_ratio": row.geometry.imbalance_ratio,
            "passes_Ekin_constraint": ekin_feasible,
            "passes_Q_constraint": q_feasible,
            "failure_mode": failure_mode,
        },
        config,
    )


def _baseline_row(
    n_value: float,
    alpha: float,
    baseline,
    strongest_type: str | None,
    config: ProtocolConfig,
) -> dict[str, object]:
    candidate = baseline.candidate
    extras = dict(baseline.extras)
    return add_report_metadata(
        {
            "n": n_value,
            "alpha": alpha,
            "baseline_type": baseline.baseline_type,
            "feasible": baseline.feasible,
            "S_Kwant": baseline.s_kwant,
            "a": "" if candidate is None else candidate.a,
            "b": "" if candidate is None else candidate.b,
            "aspect_ratio": "" if candidate is None else candidate.aspect_ratio,
            "Ekin_Kwant": "" if candidate is None else candidate.ekin_kwant,
            "Q_Kwant": "" if candidate is None else candidate.q_kwant,
            "geometry_hash": "" if candidate is None else candidate.geometry.geometry_hash,
            "N_sites": "" if candidate is None else candidate.geometry.n_sites,
            "failure_modes": " ".join(baseline.failure_modes),
            "notes": baseline.notes,
            "is_strongest_feasible_baseline": baseline.baseline_type == strongest_type,
            "S_random_best_of_5_primary": extras.get("S_random_best_of_5_primary", ""),
            "S_random_best_of_5_p75": extras.get("S_random_best_of_5_p75", ""),
            "n_feasible_repeats": extras.get("n_feasible_repeats", ""),
        },
        config,
    )


def _random_row(
    n_value: float,
    alpha: float,
    repeat_index: int,
    seed: int,
    sample_index: int,
    aspect_ratio: float,
    config: ProtocolConfig,
    q_iso: float,
    candidate: VerifiedSCandidate | None = None,
    failure_mode: str = "ok",
    repeat_best_s: float | str = "",
    random_primary: float | str = "",
    random_p75: float | str = "",
) -> dict[str, object]:
    feasible = False
    if candidate is not None:
        feasible = is_ekin_feasible(candidate, candidate.ekin_target, config) and is_q_feasible(candidate, q_iso, alpha)
    return add_report_metadata(
        {
            "n": n_value,
            "alpha": alpha,
            "repeat_index": repeat_index,
            "seed": seed,
            "sample_index": sample_index,
            "aspect_ratio": aspect_ratio,
            "a": "" if candidate is None else candidate.a,
            "b": "" if candidate is None else candidate.b,
            "feasible": feasible,
            "S_Kwant": "" if candidate is None else candidate.s_kwant,
            "Q_Kwant": "" if candidate is None else candidate.q_kwant,
            "Ekin_Kwant": "" if candidate is None else candidate.ekin_kwant,
            "geometry_hash": "" if candidate is None else candidate.geometry.geometry_hash,
            "repeat_best_S": repeat_best_s,
            "S_random_best_of_5_primary": random_primary,
            "S_random_best_of_5_p75": random_p75,
            "failure_mode": failure_mode if candidate is None or not feasible else "ok",
        },
        config,
    )


def _summary_row(
    evaluation: SingleNPassEvaluation,
    best_method: VerifiedSCandidate | None,
    alpha: float,
    q_iso: float,
    beat_simple: bool,
    classification: str,
    config: ProtocolConfig,
) -> dict[str, object]:
    return add_report_metadata(
        {
            "n": evaluation.n,
            "alpha": alpha,
            "passed": evaluation.passed,
            "best_method_candidate_rank": "" if best_method is None or best_method.candidate_rank is None else best_method.candidate_rank,
            "best_method_aspect_ratio": "" if best_method is None else best_method.aspect_ratio,
            "best_method_a": "" if best_method is None else best_method.a,
            "best_method_geometry_hash": "" if best_method is None else best_method.geometry.geometry_hash,
            "best_method_Q_Kwant": "" if best_method is None else best_method.q_kwant,
            "best_method_S_Kwant": "" if best_method is None else best_method.s_kwant,
            "Q_iso_Kwant": q_iso,
            "S_candidate_Kwant": evaluation.s_candidate,
            "S_strongest_baseline": evaluation.s_strongest_baseline,
            "delta_S_min": evaluation.delta_s_min,
            "strongest_baseline_type": evaluation.strongest_baseline_type,
            "beat_strongest_baseline": evaluation.passed,
            "beat_simple_anisotropy_heuristic": beat_simple,
            "failure_modes": " ".join(evaluation.failure_modes),
            "notes": " | ".join(evaluation.notes),
            "classification": classification,
        },
        config,
    )


def _write_readme(
    path: Path,
    primary_summary: dict[str, object],
    secondary_summary: dict[str, object],
    summary_rows: list[dict[str, object]],
) -> None:
    lines = [
        "# S-objective execution report",
        "",
        "This report is the preregistered S-objective execution under the frozen",
        "protocol. It tests whether surrogate-guided screening adds nontrivial",
        "value beyond strong physics-based baselines. It does not claim discovery",
        "of anisotropy-induced splitting.",
        "",
        "## Frozen decision rules",
        "",
        "- Primary alpha: `0.95`.",
        "- Secondary alpha: `0.90`; secondary results cannot override primary failure.",
        "- Primary success: all 4 fixed `n` values pass at alpha `0.95`.",
        "- Partial support: exactly 3/4 fixed `n` values pass at alpha `0.95`.",
        "- Exploratory / shape-dependent: 1-2/4 fixed `n` values pass at alpha `0.95`.",
        "- Negative result: 0/4 fixed `n` values pass at alpha `0.95`.",
        "- Beating isotropic same-`n` alone is insufficient.",
        "- Failure to beat the simple anisotropy heuristic means S behaves as a monotonic anisotropy diagnostic, not inverse-screening success.",
        "",
        "## Outputs",
        "",
        "- `s_candidates_verified.csv`: direct-Kwant method candidates.",
        "- `baselines_by_n.csv`: direct-Kwant or already Kwant-computed baselines.",
        "- `random_baseline_repeats.csv`: deterministic random best-of-5 repeats.",
        "- `summary_by_n.csv`: frozen pass/fail classifications.",
        "- `execution_audit.md`: execution provenance and warnings.",
        "",
        "Plots were not generated in this execution. This avoids delaying the",
        "frozen-rule run for presentation work; the CSV outputs are the primary",
        "record.",
        "",
        "## Conclusions",
        "",
        f"- Primary alpha result: {primary_summary['support_level']} "
        f"({primary_summary['primary_n_passed']}/{primary_summary['primary_n_evaluated']} passed).",
        f"- Secondary alpha result: {secondary_summary['support_level']} "
        f"({secondary_summary['primary_n_passed']}/{secondary_summary['primary_n_evaluated']} passed under alpha=0.90 evaluation).",
        "",
    ]
    if primary_summary["support_level"] != "primary success" and secondary_summary["primary_n_passed"] > primary_summary["primary_n_passed"]:
        lines.append(
            "Secondary evidence suggests possible S-control only under relaxed Q-preservation."
        )
        lines.append("")
    lines.extend(["## Per-n summary", ""])
    for row in summary_rows:
        if float(row["alpha"]) != 0.95:
            continue
        note = row["notes"]
        lines.append(
            f"- n={row['n']}: pass={row['passed']}; strongest={row['strongest_baseline_type']}; "
            f"beat_simple={row['beat_simple_anisotropy_heuristic']}; {note}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_final_execution(dataset: dict[str, np.ndarray], config: ProtocolConfig) -> dict[str, object]:
    start = time.perf_counter()
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    alpha_values = (config.alpha_primary, config.alpha_secondary)
    aspect_grid = default_aspect_ratio_grid(config)
    verification_cache: dict[str, VerifiedSCandidate] = {}
    candidate_rows: list[dict[str, object]] = []
    baseline_rows: list[dict[str, object]] = []
    random_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    evaluations: list[SingleNPassEvaluation] = []
    command_notes: list[str] = []

    for n_value in config.n_values:
        model_ekin, model_de1, model_de2, rows = train_s_surrogates_for_n(dataset, n_value)
        ekin_target = float(np.median(rows["Ekin"]))
        raw_candidates: list[SCandidate] = []
        for ar_value in aspect_grid:
            cand = solve_candidate_at_aspect_ratio(
                n_value=n_value,
                aspect_ratio=float(ar_value),
                ekin_target=ekin_target,
                model_ekin=model_ekin,
                model_de1=model_de1,
                model_de2=model_de2,
                config=config,
                candidate_type="grid_iso_ekin_candidate",
            )
            if cand is not None:
                raw_candidates.append(cand)

        iso_baseline = isotropic_same_n_reference(n_value, ekin_target, model_ekin, model_de1, model_de2, config)
        if not iso_baseline.feasible or iso_baseline.candidate is None:
            raise RuntimeError(f"Isotropic same-n reference is infeasible for n={n_value}.")
        q_iso = iso_baseline.candidate.q_kwant
        training_rows = verified_training_rows_for_n(dataset, n_value)
        verified_grid = [_verified_with_cache(cand, verification_cache) for cand in raw_candidates]

        random_candidates_by_seed: dict[int, list[VerifiedSCandidate]] = {}
        random_candidate_metadata: dict[int, list[tuple[int, float, VerifiedSCandidate | None, str]]] = {}
        for repeat_index, seed in enumerate(range(config.random_base_seed, config.random_base_seed + config.n_random_repeats)):
            random_candidates_by_seed[seed] = []
            random_candidate_metadata[seed] = []
            for sample_index, ar_value in enumerate(random_aspect_ratio_draws(seed, config), start=1):
                cand = solve_candidate_at_aspect_ratio(
                    n_value=n_value,
                    aspect_ratio=float(ar_value),
                    ekin_target=ekin_target,
                    model_ekin=model_ekin,
                    model_de1=model_de1,
                    model_de2=model_de2,
                    config=config,
                    candidate_type="random_best_of_5_member",
                    candidate_rank=sample_index,
                )
                if cand is None:
                    random_candidate_metadata[seed].append((sample_index, float(ar_value), None, "no_ekin_root"))
                    continue
                verified = _verified_with_cache(cand, verification_cache)
                random_candidates_by_seed[seed].append(verified)
                random_candidate_metadata[seed].append((sample_index, float(ar_value), verified, "ok"))

        for alpha in alpha_values:
            selected, threshold, proposal_failure = select_alpha_aware_top_k_candidates(
                raw_candidates,
                q_iso_pred=solve_candidate_at_aspect_ratio(
                    n_value=n_value,
                    aspect_ratio=config.random_aspect_ratio_max,
                    ekin_target=ekin_target,
                    model_ekin=model_ekin,
                    model_de1=model_de1,
                    model_de2=model_de2,
                    config=config,
                    candidate_type="isotropic_same_n_pred_reference",
                ).q_pred,
                alpha=alpha,
                config=config,
            )
            verified_method = [_verified_with_cache(cand, verification_cache) for cand in selected]
            feasible_method = [
                row for row in verified_method
                if is_ekin_feasible(row, ekin_target, config) and is_q_feasible(row, q_iso, alpha)
            ]
            best_method = max(feasible_method, key=lambda row: row.s_kwant) if feasible_method else None

            for row in verified_method:
                candidate_rows.append(_candidate_row(row, alpha, q_iso, config))

            training_baseline = best_training_baseline_under_constraints(training_rows, ekin_target, q_iso, alpha, config)
            random_baseline = random_best_of_5_baseline_from_repeats(
                random_candidates_by_seed,
                ekin_target=ekin_target,
                q_iso=q_iso,
                alpha=alpha,
                config=config,
            )
            simple_baseline = simple_anisotropy_heuristic_baseline(verified_grid, ekin_target, q_iso, alpha, config)
            baselines = [iso_baseline, training_baseline, random_baseline, simple_baseline]
            strongest = select_strongest_feasible_baseline(baselines).strongest
            strongest_type = None if strongest is None else strongest.baseline_type
            for baseline in baselines:
                baseline_rows.append(_baseline_row(n_value, alpha, baseline, strongest_type, config))

            random_primary = random_baseline.extras.get("S_random_best_of_5_primary", "") if random_baseline.feasible else ""
            random_p75 = random_baseline.extras.get("S_random_best_of_5_p75", "") if random_baseline.feasible else ""
            for repeat_index, seed in enumerate(range(config.random_base_seed, config.random_base_seed + config.n_random_repeats)):
                rows_for_seed = random_candidates_by_seed[seed]
                feasible_for_seed = [
                    row for row in rows_for_seed
                    if is_ekin_feasible(row, ekin_target, config) and is_q_feasible(row, q_iso, alpha)
                ]
                repeat_best = max((row.s_kwant for row in feasible_for_seed), default="")
                for sample_index, ar_value, candidate, failure_mode in random_candidate_metadata[seed]:
                    random_rows.append(
                        _random_row(
                            n_value=n_value,
                            alpha=alpha,
                            repeat_index=repeat_index,
                            seed=seed,
                            sample_index=sample_index,
                            aspect_ratio=ar_value,
                            config=config,
                            q_iso=q_iso,
                            candidate=candidate,
                            failure_mode=failure_mode,
                            repeat_best_s=repeat_best,
                            random_primary=random_primary,
                            random_p75=random_p75,
                        )
                    )

            if best_method is None:
                selection = select_strongest_feasible_baseline(baselines)
                strongest_baseline = selection.strongest
                evaluation = SingleNPassEvaluation(
                    n=float(n_value),
                    alpha=float(alpha),
                    passed=False,
                    strongest_baseline_type=None if strongest_baseline is None else strongest_baseline.baseline_type,
                    s_candidate=np.nan,
                    s_strongest_baseline=np.nan if strongest_baseline is None else strongest_baseline.s_kwant,
                    delta_s_min=np.nan if strongest_baseline is None else config.delta_s_min(strongest_baseline.s_kwant),
                    failure_modes=("no_direct_kwant_verified_method_candidate_feasible", proposal_failure),
                    notes=(),
                )
            else:
                evaluation = evaluate_single_n_pass(best_method, baselines, alpha, config, q_iso=q_iso)
            evaluations.append(evaluation)
            simple = next(base for base in baselines if base.baseline_type == "simple_anisotropy_heuristic")
            beat_simple = bool(
                best_method is not None
                and simple.feasible
                and best_method.s_kwant > simple.s_kwant + (evaluation.delta_s_min if np.isfinite(evaluation.delta_s_min) else 0.0)
            )
            classification = "pass" if evaluation.passed else "fail"
            summary_rows.append(_summary_row(evaluation, best_method, alpha, q_iso, beat_simple, classification, config))
            command_notes.append(
                f"n={n_value}, alpha={alpha}: selected={len(selected)}, feasible_method={len(feasible_method)}, "
                f"pass={evaluation.passed}, strongest={evaluation.strongest_baseline_type}"
            )

    primary_summary = summarize_across_n(evaluations, config)
    secondary_config = replace(config, alpha_primary=config.alpha_secondary)
    secondary_summary = summarize_across_n(evaluations, secondary_config)

    _write_csv(output_dir / "s_candidates_verified.csv", candidate_rows, S_CANDIDATES_VERIFIED_COLUMNS + ["passes_Ekin_constraint", "passes_Q_constraint"])
    _write_csv(
        output_dir / "baselines_by_n.csv",
        baseline_rows,
        BASELINES_BY_N_COLUMNS
        + ["a", "b", "aspect_ratio", "Ekin_Kwant", "Q_Kwant", "N_sites", "is_strongest_feasible_baseline", "S_random_best_of_5_primary", "S_random_best_of_5_p75", "n_feasible_repeats"],
    )
    _write_csv(
        output_dir / "random_baseline_repeats.csv",
        random_rows,
        RANDOM_BASELINE_REPEATS_COLUMNS + ["b", "Q_Kwant", "Ekin_Kwant", "geometry_hash", "repeat_best_S", "S_random_best_of_5_primary", "S_random_best_of_5_p75"],
    )
    _write_csv(
        output_dir / "summary_by_n.csv",
        summary_rows,
        SUMMARY_BY_N_COLUMNS
        + ["best_method_candidate_rank", "best_method_aspect_ratio", "best_method_a", "best_method_geometry_hash", "best_method_Q_Kwant", "Q_iso_Kwant", "beat_strongest_baseline", "beat_simple_anisotropy_heuristic", "classification"],
    )
    _write_readme(output_dir / "README.md", primary_summary, secondary_summary, summary_rows)
    runtime = time.perf_counter() - start
    return {
        "runtime_seconds": runtime,
        "primary_summary": primary_summary,
        "secondary_summary": secondary_summary,
        "summary_rows": summary_rows,
        "command_notes": command_notes,
        "n_candidate_rows": len(candidate_rows),
        "n_random_rows": len(random_rows),
        "n_baseline_rows": len(baseline_rows),
    }


def _implementation_audit_text(config: ProtocolConfig) -> str:
    schemas = "\n".join(f"- {name}: {len(columns)} columns prepared" for name, columns in FUTURE_OUTPUT_SCHEMAS.items())
    return "\n".join(
        [
            "# S-objective implementation audit",
            "",
            "This file documents the implementation scaffolding only. No full",
            "S-objective experiment was run for this commit, and no final S outputs",
            "were produced.",
            "",
            "## Frozen protocol constants encoded",
            "",
            f"- preregistration_commit: {config.preregistration_commit}",
            f"- protocol_branch: {config.protocol_branch}",
            f"- implementation_branch: {config.implementation_branch}",
            f"- n_values: {list(config.n_values)}",
            f"- alpha_primary: {config.alpha_primary}",
            f"- alpha_secondary: {config.alpha_secondary}",
            f"- ekin_tolerance_rel: {config.ekin_tolerance_rel}",
            f"- top_k_candidates: {config.top_k_candidates}",
            f"- jaccard_non_distinct_threshold: {config.jaccard_non_distinct_threshold}",
            f"- random_base_seed: {config.random_base_seed}",
            f"- n_random_repeats: {config.n_random_repeats}",
            f"- random_aspect_ratio_min: {config.random_aspect_ratio_min}",
            f"- random_aspect_ratio_max: {config.random_aspect_ratio_max}",
            "- delta_s_min: max(0.02 * S_strongest_baseline, 1e-3)",
            "",
            "## Implemented scaffolding",
            "",
            "- frozen ProtocolConfig and runtime assertion of preregistered constants;",
            "- discrete-site geometry hashing from sorted integer Kwant lattice coordinates;",
            "- Jaccard site-set overlap for non-distinct candidate detection;",
            "- Ekin target computation as median(Ekin) for fixed n training rows;",
            "- S/Q computation and direct Kwant verification helper;",
            "- Ekin and Q feasibility checks;",
            "- top-5 diverse method-candidate selection;",
            "- random baseline sampling of aspect_ratio only, with a determined by the same Ekin-root procedure;",
            "- strongest feasible baseline selection with explicit infeasible-baseline reporting;",
            "- single-n and across-n pass/fail classification;",
            "- metadata columns required for future final reports and summaries.",
            "",
            "## Future output schemas prepared",
            "",
            schemas,
            "",
            "## Not run / not produced",
            "",
            "- no full S-objective experiment;",
            "- no final candidate CSV;",
            "- no final baseline CSV;",
            "- no random-baseline repeats CSV;",
            "- no summary_by_n CSV;",
            "- no plots;",
            "- no article text;",
            "- no thesis changes.",
            "",
            "## Limitations",
            "",
            "- Full result writing remains intentionally disabled until explicit execution approval.",
            "- Capped smoke verification can run direct Kwant only when --max-kwant-per-n is set.",
            "- Plot generation is schema-planned but not implemented in this scaffolding commit.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = ProtocolConfig()
    assert_frozen_protocol_constants(config)

    dataset = load_superellipse_dataset(DATA_PATH)
    targets = compute_ekin_targets(dataset, n_values=config.n_values)
    print(f"Frozen preregistration commit: {config.preregistration_commit}")
    print(f"Ekin targets: {targets}")
    print(f"Future output schemas: {', '.join(FUTURE_OUTPUT_SCHEMAS)}")
    if args.run_final:
        print("Final S-output writing is enabled by explicit --run-final.")
    else:
        print("Final S-output writing is disabled unless --run-final is provided.")

    if args.write_implementation_audit:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "implementation_audit.md").write_text(_implementation_audit_text(config), encoding="utf-8")

    if args.training_q_diagnostics:
        print("Training Q(aspect_ratio) diagnostics:")
        for row in training_q_by_aspect_ratio_diagnostics(dataset, config):
            print(row)

    if args.proposal_diagnostics:
        print("Alpha-aware proposal diagnostics:")
        for diag in alpha_aware_proposal_diagnostics(dataset, config):
            print(diag)

    if args.run_final:
        result = _run_final_execution(dataset, config)
        print(f"Final execution runtime_seconds={result['runtime_seconds']:.3f}")
        print(f"Primary summary: {result['primary_summary']}")
        print(f"Secondary summary: {result['secondary_summary']}")
        for note in result["command_notes"]:
            print(note)
        print(
            f"Rows written: candidates={result['n_candidate_rows']}, "
            f"baselines={result['n_baseline_rows']}, random={result['n_random_rows']}"
        )
        return 0

    if args.dry_run and args.max_kwant_per_n <= 0:
        return 0

    if args.max_kwant_per_n > 0:
        grid = default_aspect_ratio_grid(config)
        for n_value in config.n_values:
            candidates, _, _ = generate_method_candidates_for_n(dataset, n_value, config, aspect_ratio_grid=grid)
            limit = min(args.max_kwant_per_n, len(candidates))
            verified = [verify_candidate_kwant(cand) for cand in candidates[:limit]]
            finite_s = [row.s_kwant for row in verified if np.isfinite(row.s_kwant)]
            print(f"n={n_value}: smoke_kwant={len(verified)}, finite_S={len(finite_s)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

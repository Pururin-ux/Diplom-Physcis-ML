"""Thin runner for S-objective screening scaffolding.

This implementation-stage runner validates the frozen protocol and can perform
dry-run/capped smoke checks. It intentionally does not write final scientific
S-objective outputs in this commit.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.s_objective_screening import (  # noqa: E402
    FUTURE_OUTPUT_SCHEMAS,
    ProtocolConfig,
    alpha_aware_proposal_diagnostics,
    assert_frozen_protocol_constants,
    compute_ekin_targets,
    default_aspect_ratio_grid,
    generate_method_candidates_for_n,
    training_q_by_aspect_ratio_diagnostics,
    train_s_surrogates_for_n,
    verify_candidate_kwant,
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
    return parser


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
    print("Final S-output writing is disabled in this implementation commit.")

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

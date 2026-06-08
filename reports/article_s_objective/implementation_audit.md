# S-objective implementation audit

This file documents the implementation scaffolding only. No full S-objective
experiment was run for this commit, and no final S outputs were produced.

## Frozen protocol constants encoded

- preregistration_commit: `7e28542fda40db288ad2613b49f17b1248f6f2ce`
- protocol_branch: `article-s-objective-preregistration`
- implementation_branch: `article-s-objective-implementation`
- `n_values = [1.2, 2.0, 3.0, 4.0]`
- `alpha_primary = 0.95`
- `alpha_secondary = 0.90`
- `ekin_tolerance_rel = 0.05`
- `top_k_candidates = 5`
- `jaccard_non_distinct_threshold = 0.99`
- `random_base_seed = 20260602`
- `n_random_repeats = 50`
- `random_aspect_ratio_min = 0.67`
- `random_aspect_ratio_max = 1.0`
- `delta_s_min = max(0.02 * S_strongest_baseline, 1e-3)`

## Implemented scaffolding

- frozen `ProtocolConfig` and runtime assertion of preregistered constants;
- discrete-site geometry hashing from sorted integer Kwant lattice coordinates;
- Jaccard site-set overlap for non-distinct candidate detection;
- `Ekin_target(n) = median(Ekin)` over already Kwant-computed training rows for fixed `n`;
- S/Q computation and direct Kwant verification helper;
- Ekin and Q feasibility checks;
- top-5 diverse method-candidate selection;
- random baseline sampling of `aspect_ratio` only, with `a` determined by the same Ekin-root procedure;
- strongest feasible baseline selection with explicit infeasible-baseline reporting;
- single-`n` and across-`n` pass/fail classification;
- metadata columns required for future final reports and summaries.

## Not run / not produced

- no full S-objective experiment;
- no final candidate CSV;
- no final baseline CSV;
- no random-baseline repeats CSV;
- no `summary_by_n.csv`;
- no plots;
- no article text;
- no thesis changes.

## Limitations

- Full result writing remains intentionally disabled until explicit execution approval.
- Capped smoke verification can run direct Kwant only when `--max-kwant-per-n` is set.
- Plot generation is schema-planned but not implemented in this scaffolding commit.

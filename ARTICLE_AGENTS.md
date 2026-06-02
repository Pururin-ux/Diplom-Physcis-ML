# Article Extension Instructions

## Scope

The thesis/diploma results are already complete and must not be silently
rewritten. This branch is for an article-level falsification experiment.

The only allowed article extension is surrogate-guided inverse spectral
screening inside the already verified fixed-discrete-`n` superellipse domain:

- `a in [24, 36]`
- `aspect_ratio in [0.67, 1.0]`
- `n in {1.2, 2.0, 3.0, 4.0}`

This is not closed-loop inverse design unless an iterative retraining loop is
implemented. The current article-extension experiment is one-shot screening.

## Scientific Rules

- Direct Kwant calculation remains the source of truth.
- Surrogate predictions are candidate generators only.
- Continuous surrogate parameters induce discrete lattice geometries in Kwant.
- Final reported values must be Kwant-verified.
- Negative results are valid and must not be hidden.
- Do not compare Kwant-verified candidates against non-verified surrogate
  baselines.
- Do not call the isotropic same-`n` baseline a circle baseline except for
  `n = 2.0`.
- Do not overclaim novelty or performance.
- Do not treat surrogate predictions as physical truth.
- Do not claim material-specific relevance without material-specific
  calibration.
- Future S-objective screening must be pre-registered before implementation or
  execution.
- Future S-objective work must include Q preservation constraints and/or Q-S
  Pareto analysis; bare maximization of S is not sufficient because it can
  collapse to "maximum anisotropy wins".
- S-objective implementation must follow the frozen rules in
  `reports/article_s_objective/preregistration_protocol.md`. Do not change
  alpha values, Ekin target definition, Ekin tolerance, baseline hierarchy,
  random-baseline seeds/repeat count, random sampling domain, top-5 candidate
  selection rule, diversity criterion, pass definition, or `delta_S_min` after
  seeing results. Beating isotropic same-`n` alone is not sufficient for
  inverse-screening success; the candidate must beat the strongest feasible
  baseline and the simple anisotropy heuristic. Any post-freeze amendment
  requires a new dated preregistration commit and cannot apply retroactively.
- For S-objective implementation, `geometry_hash` must be computed from the
  realized discrete Kwant site set using stable sorted integer lattice
  coordinates, not from continuous `(a, aspect_ratio, n)` parameters. The
  preregistered random baseline samples `aspect_ratio` from `Uniform(0.67, 1.0)`
  and then determines `a` by the same Ekin-target procedure as method
  candidates; independently sampling `a` is only an explicitly labeled stress
  test. If the method does not beat the smallest-feasible-`aspect_ratio`
  heuristic, report S as a monotonic anisotropy diagnostic rather than
  inverse-design success.

## Exclusions

- No DFT/OpenMX.
- No CNN/GNN/neural operators.
- No arbitrary new shape families.
- No literature benchmark validation.
- No `a > 36` in the main test.
- No modification of thesis chapters or thesis conclusions.

## Engineering Rules

- Put reusable logic in `src/`.
- Keep scripts and notebooks thin.
- Add or update tests for important logic.
- Keep article-extension outputs under the specific `reports/article_*`
  directory for that experiment or protocol.
- Never hide failure modes or negative results.

## AI-Research-SKILLs use policy

- AI-Research-SKILLs are agent-side aids, not scientific methods.
- They must not replace direct Kwant verification.
- They must not weaken the independent audit requirement.
- They must not be used to inflate claims or turn negative results into
  positive narratives.
- Relevant skills may be used for literature search, research planning, rigor
  review, plotting, experiment tracking, and paper drafting after results are
  scientifically valid.
- Irrelevant LLM-engineering skills should not be used for this physics project.
- Any advice from skills must be checked against the repository, data, and
  direct solver results.

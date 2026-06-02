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
- Keep outputs for this branch under `reports/article_inverse_screening/`.
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

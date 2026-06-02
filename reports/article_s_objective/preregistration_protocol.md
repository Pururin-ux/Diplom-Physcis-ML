# S-objective screening preregistration protocol

## Status

This document pre-registers a possible article-extension experiment. It is not
an experiment report, not an optimization result, and not a change to the
completed thesis. No S-objective screening has been run in this protocol.

## Motivation

The prior Q-objective one-shot surrogate-guided screening failed as an inverse
screening result. For every tested fixed `n`, the selected best candidate
collapsed to the isotropic same-`n` geometry and did not beat the isotropic
Kwant-verified baseline.

The symmetry-optimum analysis and the direct near-isotropy Kwant sweep support
the interpretation that `Q = dE1 / Ekin` increases toward the isotropic
same-`n` geometry, while the normalized excited-doublet splitting
`S = (E2 - E1) / Ekin` decreases toward isotropy. The near-isotropy sweep also
showed that strict isotropic optimality in Q is ambiguous at the rasterized
lattice-noise scale, but it did not rescue the original Q-screening hypothesis.

Therefore, S is a possible next objective only if it is treated as a new,
pre-registered hypothesis. S is not a post hoc success criterion for the failed
Q objective.

## Definitions

For direct Kwant eigenvalues `E0`, `E1`, `E2`, and `E3`:

- `Ekin = E0 + 4`
- `dE1 = E1 - E0`
- `dE2 = E2 - E1`
- `Q = dE1 / Ekin`
- `S = dE2 / Ekin`

All final reported values must be computed from direct Kwant spectra. Surrogate
models may generate candidate roots only.

## Main Hypothesis

Boundary anisotropy can increase the normalized excited-doublet splitting `S`
at fixed kinetic-energy scale `Ekin`, while retaining a controlled fraction of
the isotropic same-`n` Q value.

This hypothesis is distinct from the failed Q-objective hypothesis. A positive
S result would not retroactively make the Q screening successful.

## Non-Trivial Objectives

A bare maximize-S objective is not scientifically sufficient because it may
reduce to selecting the most anisotropic feasible geometry. The experiment must
use at least one constrained or multi-objective formulation.

### Objective A: constrained S maximization

For each fixed `n` and target energy:

- maximize `S_Kwant`;
- require `abs(Ekin_Kwant - Ekin_target) <= epsilon_E`;
- require `Q_Kwant >= alpha * Q_iso_Kwant`;
- evaluate at least `alpha = 0.90` and `alpha = 0.95`.

`Q_iso_Kwant` is the direct Kwant value for the isotropic same-`n` baseline at
the same target-energy construction.

### Objective B: S-Q Pareto screening

At fixed `Ekin`, evaluate the Pareto frontier for:

- maximize `S_Kwant`;
- minimize `Q_loss = max(0, Q_iso_Kwant - Q_Kwant)`.

This objective is preferable if feasible points show a smooth tradeoff rather
than a single obvious constrained winner.

### Objective C: target-S screening with Q preservation

For pre-specified `S_target` values:

- find feasible candidates near `S_target`;
- require the same direct Kwant Ekin constraint;
- require Q preservation using the `alpha` thresholds above;
- rank candidates by small target-S error first, then by smaller Q loss.

This objective is useful only if `S_target` is fixed before running the
screening.

## Domain

The main experiment must stay inside the already verified fixed-discrete-`n`
superellipse domain:

- `n in {1.2, 2.0, 3.0, 4.0}`
- `a in [24, 36]`
- `aspect_ratio in [0.67, 1.0]`

Values `a > 36` are not allowed in the main test. If ever used, they must be
labeled as extrapolation or stress testing, not as main-domain evidence.

## Candidate Generation

For each `n`, use the same target-energy convention already used in the
article-extension analyses:

- `Ekin_target = median(Ekin)` within that fixed `n` training subset.

Candidate generation may use the existing surrogate iso-Ekin root procedure:

- solve for a root in `a` at each candidate `aspect_ratio`;
- keep roots only inside `a in [24, 36]`;
- build the corresponding discrete Kwant geometry;
- deduplicate candidates by `geometry_hash`.

Surrogate values may be used for candidate generation and prioritization, but
not as final evidence.

## Direct Verification

For every selected candidate and every baseline, compute direct Kwant spectra:

- `E0_Kwant`
- `E1_Kwant`
- `E2_Kwant`
- `E3_Kwant`

Then compute:

- `Ekin_Kwant`
- `dE1_Kwant`
- `dE2_Kwant`
- `Q_Kwant`
- `S_Kwant`
- `geometry_hash`
- `N_sites`
- sublattice counts and imbalance diagnostics, if available from the existing
  geometry helpers.

Exact `Ekin` equality must not be required. Continuous superellipse parameters
induce discrete lattice domains, and `Ekin_Kwant` changes stepwise.

## Baselines

All baselines used in final comparisons must be direct Kwant verified or come
from already Kwant-computed training data. Do not compare a Kwant-verified
candidate against a surrogate-only baseline.

Required baselines:

- isotropic same-`n` baseline;
- best existing training geometry under the same S/Q objective;
- feasible random best-of-5 under the same Ekin and Q constraints;
- simple anisotropy heuristic: smallest feasible `aspect_ratio` under the same
  Ekin and Q constraints.

If the method does not beat the simple anisotropy heuristic, no inverse-design
advantage claim is allowed. The result may still be reported as a monotonicity
or tradeoff result.

Do not call the isotropic same-`n` baseline a circle baseline except for
`n = 2.0`.

## Success Criteria

A per-`n` S-objective result is supported only if all of the following hold:

- the selected candidate satisfies the direct Kwant Ekin constraint;
- the selected candidate satisfies the pre-registered Q preservation threshold;
- `S_Kwant` beats all required baselines by a conservative threshold larger than
  the observed rasterization and numerical noise scale;
- the selected candidate is not merely the smallest feasible `aspect_ratio`
  unless the claim is explicitly downgraded to a monotonicity result;
- duplicate geometry hashes do not create artificial wins.

Across-`n` support requires the same criteria to hold for a pre-specified
majority or all of `n in {1.2, 2.0, 3.0, 4.0}`. The majority/all rule must be
chosen before running the experiment.

## Failure Modes

The experiment must explicitly report these failure modes if they occur:

- no feasible candidates under the Ekin and Q constraints;
- objective collapses to the minimum feasible `aspect_ratio`;
- apparent S gain disappears after direct Kwant verification;
- Q preservation threshold fails;
- candidate does not beat the best training baseline;
- candidate does not beat feasible random best-of-5;
- candidate does not beat the simple anisotropy heuristic;
- duplicate discrete geometries hide the true number of independent candidates;
- Ekin mismatch or boundary rasterization is larger than the claimed S gain;
- surrogate ranking error drives candidate selection.

## Expected Outputs

If the experiment is implemented later, outputs should be placed under
`reports/article_s_objective/` and include:

- candidate CSV with surrogate-generation metadata and direct Kwant fields;
- `summary_by_n.csv`;
- S versus `aspect_ratio` plots;
- Q versus S Pareto plots;
- E-level splitting plots.

The output README must distinguish direct Kwant evidence from surrogate
candidate generation.

## Allowed Claims

Allowed only if supported by the pre-registered success criteria:

- boundary anisotropy increases the verified normalized excited-doublet
  splitting S under fixed-domain and fixed-Ekin constraints;
- the selected S candidates preserve Q above the pre-registered threshold;
- the S objective has a non-trivial advantage over the simple anisotropy
  heuristic.

Allowed if the experiment fails:

- the S objective was not supported under the tested constraints;
- S behaves mostly as a monotonic anisotropy diagnostic rather than an inverse
  screening objective;
- the feasible domain or Q-preservation constraint is too restrictive for this
  objective.

## Forbidden Claims

The experiment must not claim:

- closed-loop inverse design;
- that surrogate predictions are physical truth;
- that a positive S result rescues the failed Q-objective result;
- material-specific relevance without material-specific calibration;
- article-level novelty or performance if the method only follows the simple
  anisotropy heuristic;
- success from weak or surrogate-only baselines;
- that negative or ambiguous outcomes are positive inverse-design evidence.

## Narrative Implications

Before any S screening is run, the scientific narrative remains unchanged:

- the Q-objective inverse-screening run is negative;
- symmetry and near-isotropy analyses support a doublet-splitting explanation,
  with strict Q isotropic optimality ambiguous near the lattice-noise scale;
- S is justified only as a separately pre-registered objective, not as a hidden
  replacement endpoint.

# S-objective screening preregistration protocol

## Status

This document pre-registers a possible article-extension experiment. It is not
an experiment report, not an optimization result, and not a change to the
completed thesis. No S-objective screening has been run in this protocol.

## Frozen Success Rules Before Execution

### Finality of this preregistration

These rules are final after this commit.

Any amendment after this commit requires a new dated preregistration commit
with explicit justification.

No amendment may be applied retroactively to already obtained S-objective
results.

### Target energy

For each fixed `n`:

`Ekin_target(n) = median(Ekin)`

computed over all already Kwant-computed training rows with that `n`, across
all `a` and `aspect_ratio` values in the training grid.

This target-energy rule must not be changed after seeing S-screening results.

### Primary objective

Primary objective:

Objective A - constrained S maximization.

Primary alpha:

`alpha = 0.95`.

Secondary alpha:

`alpha = 0.90`.

Objective B:

Pareto analysis is exploratory/diagnostic only and cannot be promoted to a
primary claim after seeing results.

Objective C:

Not part of this study. It must not be run unless `S_target` values are fixed
in a separate preregistration before execution.

### Candidate selection rule

For each `n` and alpha setting:

- the surrogate may propose up to top-5 diverse candidates;
- candidates must be deduplicated by `geometry_hash` before final verification;
- the final method candidate is the best direct-Kwant-verified feasible
  candidate among those top-5;
- if fewer than five feasible diverse candidates exist, use the available
  feasible candidates and report the count;
- if no feasible candidate exists, that `n` fails for that alpha.

Candidate diversity rule:

Two candidates are considered non-distinct if either:

1. `geometry_hash(candidate_i) == geometry_hash(candidate_j)`
2. `Jaccard(site_set_i, site_set_j) > 0.99`

Only distinct candidates count toward the top-5 candidate budget.

If Jaccard computation is unavailable or too expensive, `geometry_hash`
deduplication is mandatory and the missing Jaccard check must be reported as a
limitation.

`geometry_hash` must be computed from the realized discrete Kwant geometry, not
from continuous parameters. Hashes based only on `(a, aspect_ratio, n)` or other
floating-point parameter tuples are forbidden.

Required construction:

1. build the discrete site set first;
2. serialize the sorted integer lattice coordinates in a stable way;
3. hash that serialization.

For example:

```text
sorted_sites = sorted((int(x), int(y)) for each lattice site)
geometry_hash = sha256(repr(sorted_sites).encode("utf-8")).hexdigest()
```

Equivalent stable byte serialization is allowed. Two continuous parameter sets
that produce the same discrete site set must have the same `geometry_hash`.

A single successful candidate among top-5 can count only because top-5
candidate selection is part of the pre-registered method.

Do not increase the number of candidates after seeing results.

### Ekin tolerance

A candidate or baseline is feasible only if:

`abs(Ekin_Kwant - Ekin_target) / Ekin_target <= 0.05`

That is, Ekin tolerance is +/-5% relative to target.

If a candidate or baseline violates this constraint, it is infeasible
regardless of S value.

### Q preservation

For primary analysis:

`Q_Kwant >= 0.95 * Q_iso_Kwant`

For secondary analysis:

`Q_Kwant >= 0.90 * Q_iso_Kwant`

where `Q_iso_Kwant` is the direct Kwant value for the isotropic same-`n`
reference at the same target-energy construction.

### Baseline hierarchy

Required baselines:

1. isotropic same-`n` reference;
2. best training row under the same Ekin/Q constraints;
3. feasible random best-of-5 under the same Ekin/Q constraints;
4. simple anisotropy heuristic: smallest feasible `aspect_ratio` under the
   same Ekin/Q constraints.

All final baseline comparisons must use direct Kwant values or already
Kwant-computed training rows.

Do not compare Kwant-verified candidates against surrogate-only baselines.

The isotropic same-`n` reference is a physical-effect baseline. It is not
sufficient as the primary inverse-screening success baseline for S.

Define:

```text
S_strongest_baseline = max(
    S_isotropic_same_n,
    S_best_training,
    S_random_best_of_5_primary,
    S_simple_anisotropy_heuristic
)
```

using only baselines that satisfy the same Ekin and Q constraints.

The strongest feasible baseline is the primary success baseline.

If the candidate beats isotropic but does not beat the strongest feasible
baseline, report: "physical doublet-splitting effect observed, but no
inverse-screening advantage."

If the candidate does not beat the simple anisotropy heuristic, no
inverse-screening advantage claim is allowed.

The simple anisotropy heuristic may dominate because S is physically expected
to grow with anisotropy. If the method does not beat the smallest-feasible-
`aspect_ratio` heuristic, report: "S behaves as a monotonic anisotropy
diagnostic rather than a non-trivial inverse-screening objective in this tested
domain." Do not reinterpret such a result as inverse-design success.

### Random baseline construction

Use fixed deterministic random seeds.

`N_random_repeats = 50`.

Use:

```text
base_seed = 20260602
seeds = base_seed + i for i = 0, 1, ..., 49
```

For each repeat:

- sample five aspect ratios from `Uniform(0.67, 1.0)`;
- for each sampled `aspect_ratio`, construct the candidate using the same
  Ekin-target construction as the surrogate-generated candidates;
- solve or select `a in [24, 36]` according to the same iso-Ekin/root/refinement
  procedure used for the method candidates;
- apply the same Ekin and Q feasibility rules;
- direct-Kwant verify candidates or use already Kwant-computed values where
  applicable;
- take the best S among the five feasible random candidates.

The random baseline randomizes shape, not physical confinement scale. The
primary random baseline must not sample `a` independently from
`Uniform(24, 36)`. Independent `a` sampling is allowed only as an explicitly
labeled stress test, not as the preregistered random baseline.

The primary random baseline is:

`S_random_best_of_5_primary = median of the 50 random-best-of-5 values`.

Also report:

`S_random_best_of_5_p75 = 75th percentile of the 50 random-best-of-5 values`.

The 75th percentile is a stricter diagnostic baseline, but the primary success
rule uses the median random-best-of-5 baseline unless this protocol is changed
before any experiment is run.

If random sampling cannot produce feasible candidates for a given `n` and
alpha, report random baseline as infeasible for that case.

### Infeasible-baseline handling

If a required baseline cannot produce any feasible candidate under the same
Ekin/Q constraints:

- mark that baseline as infeasible;
- exclude it from `S_strongest_baseline`;
- report the failure mode explicitly.

A baseline may not be silently dropped.

If the simple anisotropy heuristic is infeasible, say so explicitly. In that
case, no claim of beating the anisotropy heuristic is possible for that
`n`/alpha.

### Single-n pass definition

A fixed `n` counts as passed only if all conditions hold:

1. Candidate satisfies Ekin tolerance:
   `abs(Ekin_Kwant - Ekin_target) / Ekin_target <= 0.05`
2. Candidate satisfies Q preservation:
   `Q_Kwant >= alpha * Q_iso_Kwant`
3. Candidate beats the strongest feasible baseline by a meaningful S gain:
   `S_candidate_Kwant > S_strongest_baseline + delta_S_min`, where
   `delta_S_min = max(0.02 * S_strongest_baseline, 1e-3)`.
   Since `S = (E2 - E1) / Ekin` is dimensionless, `delta_S_min` is also
   dimensionless. Equivalently, the candidate must exceed the strongest
   feasible baseline by both relative S gain greater than 2% and absolute S
   gain greater than `1e-3`.
4. Candidate is not a duplicate discrete geometry of the winning baseline.
5. Candidate is not merely the smallest feasible `aspect_ratio` unless it also
   beats the simple anisotropy heuristic by `delta_S_min`.

If any condition fails, that `n` does not pass for the relevant alpha.

### Across-n success levels

Primary success:

All 4 `n` values pass under `alpha = 0.95`.

Partial support:

Exactly 3/4 `n` values pass under `alpha = 0.95`. Do not make a broad "method
works" claim.

Exploratory / shape-dependent:

Only 1-2/4 `n` values pass. Report as shape-dependent or exploratory only.

Negative result:

0/4 `n` values pass.

Secondary support:

Results under `alpha = 0.90` are secondary and cannot override primary
`alpha = 0.95` failure.

### Rasterization/noise handling

Do not introduce a post-hoc `sigma_raster` into the primary success rule after
seeing results.

The primary threshold is fixed as:

`delta_S_min = max(0.02 * S_strongest_baseline, 1e-3)`

Rasterization/noise diagnostics may be reported as secondary analysis, but they
cannot be used to relax the preregistered success criteria.

### Failure modes

Explicitly report:

- no feasible candidate;
- fewer than five diverse candidates available;
- Ekin tolerance failed;
- Q preservation failed;
- candidate beats isotropic only;
- candidate does not beat strongest feasible baseline;
- candidate does not beat simple anisotropy heuristic;
- required baseline infeasible;
- random baseline infeasible;
- candidate is duplicate geometry;
- candidate diversity check failed or was incomplete;
- apparent gain is below `delta_S_min`;
- result collapses to monotonic anisotropy heuristic;
- surrogate ranking fails after direct Kwant verification.

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

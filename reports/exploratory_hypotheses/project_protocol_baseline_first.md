# Baseline-First Project Protocol

## Status

This protocol is the working rule for future exploratory physics/ML work in
this repository.

The purpose is to prevent weak novelty claims, textbook rediscoveries, and ML
results that only learn size, symmetry, discretization, or geometry proxies.

## Current Closed Lines

### Q inverse screening

Status: **CLOSED NEGATIVE**.

Reason: the objective is biased toward isotropy / simple same-n baselines.
Candidate generation did not provide a non-baseline inverse-design signal.

### S objective

Status: **CLOSED NEGATIVE**.

Reason: `S = (E2 - E1) / (E0 + 4)` behaves largely as a monotonic anisotropy
diagnostic. Surrogate candidates did not beat the strongest feasible physics
baselines.

### Magnetic ranking crossover

Status: **CLOSED / KILLED_BASELINE**.

Reason: weak-field magnetic response was numerically real, but no thresholded
non-baseline ranking crossover survived the filters. Robustness-divergence
candidates were explained by circle/ellipse symmetry lifting.

### ML advantage over physics baselines

Status: **NOT DEMONSTRATED**.

Reason: physics-informed baselines remain stronger than the tested small
MLP/surrogate workflow under structured validation.

## Forbidden Novelty Claims

Do not claim novelty from:

- `1/a^2` confinement scaling;
- Weyl area/perimeter corrections;
- anisotropy splitting;
- isotropy / symmetry degeneracy lifting;
- sublattice imbalance / zero modes;
- Peierls substitution;
- Fock-Darwin / Landau physics;
- Hofstadter-butterfly narratives for finite dots;
- type-I/type-II core-shell localization;
- generic claims that shape affects spectrum;
- ML beating weak baselines only.

Known physics may be used as a baseline or confounder, but not as the claimed
contribution.

## Baseline Ladder

Every new hypothesis must be tested against the simplest plausible physical
explanation before ML is allowed.

Baseline ladder:

1. size / area / `N_sites`;
2. `1/a^2` confinement;
3. aspect ratio / anisotropy;
4. isotropy / symmetry degeneracy;
5. perimeter / Weyl-type correction;
6. lattice discretization;
7. sublattice imbalance;
8. perturbation theory;
9. direct Kwant verification;
10. only then ML.

If the idea dies at any level, stop and record the failure condition.

## Valid Hypothesis Format

Every future exploratory hypothesis must state, before execution:

- what is fixed;
- what is varied;
- what is measured;
- what physical mechanism is being tested;
- what textbook or prior-art result could already explain it;
- which baseline could kill it;
- what result counts as `KILLED`;
- what result counts as `INTERESTING`;
- what result would be required before any ML/surrogate work.

A direction that cannot be quickly killed is not yet formulated precisely
enough.

## Signal Acceptance Rule

A candidate signal is not accepted unless it:

- survives the strongest baseline subtraction or comparison;
- survives structured validation, not only random train/test splits;
- survives size or discretization checks when relevant;
- is not explained by symmetry leakage;
- is not a one-n anecdote unless explicitly framed as a narrow effect;
- gives qualitative physical information, not only a small metric improvement;
- is confirmed by direct Kwant calculation before any ML claim.

## ML Rule

ML is allowed only after direct physics tests show a nontrivial residual that is
not absorbed by the baseline ladder.

Do not ask:

> Can ML predict this?

Ask instead:

> What is the smallest physical explanation that predicts this almost as well?

If that explanation exists, ML is not the result. At most, ML may be a
convenience layer or a negative benchmark.

## Project Framing Rule

Current safe framing:

> In the tested superellipse tight-binding family, low-energy spectral design
> objectives are dominated by simple physical baselines. ML advantage and
> magnetic ranking-crossover advantage were not demonstrated under structured,
> baseline-first tests.

Forbidden reframings:

- do not claim inverse-design success;
- do not claim magnetic design success;
- do not claim ML advantage;
- do not claim lattice-residual novelty without a new continuum/dense-grid
  protocol;
- do not use a closed negative branch as a positive lead.

## Future Work Rule

Any future work on a closed line requires a new exploratory protocol branch and
a new preregistered failure condition.

In particular:

- future magnetic work must exclude circle-driven degeneracy effects from the
  primary signal definition;
- future lattice-residual work must distinguish itself from
  Weyl/perimeter/discretization baselines;
- future defect work must beat perturbation-theory baselines;
- future core-shell work must beat radial/core-size/shell-thickness baselines;
- future ML work must begin only after a direct non-baseline physical residual
  exists.

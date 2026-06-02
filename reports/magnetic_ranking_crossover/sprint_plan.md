# Magnetic Ranking-Crossover Sprint Plan

## Purpose

Run a minimal direct-Kwant exploratory sprint to test whether weak perpendicular
magnetic flux changes the ordering of a small, fixed set of superellipse quantum
dots by low-energy spectral gaps.

This sprint is exploratory only. It is not a machine-learning task, not inverse
screening, not an S-objective rescue run, and not an article-ready novelty
claim.

## Why This Is Not Q/S Rescue

The Q/S inverse-screening line is already closed as a negative result under the
frozen protocol. Q was biased toward isotropy, and S behaved as a monotonic
anisotropy diagnostic in the tested superellipse domain. This sprint does not
modify those outputs, conclusions, or preregistration files. It asks a different
exploratory question: whether weak magnetic flux changes geometry rankings by
raw low-energy gaps.

## Why Magnetic Field Is Not Automatically Novel

Magnetic field changing energy levels is expected physics. Peierls substitution,
Kwant gauge implementation, Fock-Darwin/Landau-type intuition, and circular
symmetry splitting are all baselines or sanity checks, not novelty. A meaningful
signal would require a weak-field, gauge-invariant, size-stable ranking
crossover or robustness divergence not explained by the simple baselines below.

## Exact Hypothesis

At zero magnetic field, low-energy spectral objectives are dominated by simple
geometry baselines. Under weak magnetic flux, the ordering of superellipse
geometries by low-energy gaps may change. A meaningful signal is a weak-field,
gauge-invariant, size-stable ranking crossover or robustness divergence that
cannot be reduced to circle, ellipse, aspect-ratio, or symmetry-lifting
baselines.

## Non-Novel Physics List

- Peierls substitution itself is not novel.
- Magnetic field changing energy levels is not novel.
- Gauge implementation in Kwant is not novel.
- Fock-Darwin / Landau physics are baselines.
- Hofstadter butterfly is not an explanation for finite dots in this sprint.
- Symmetry splitting of circular-dot degeneracies is a baseline/artifact
  candidate.
- ML/surrogate advantage is not claimed.

## Gauge Conventions

Magnetic field is encoded by flux per plaquette:

```text
alpha = flux per plaquette / flux quantum
```

Primary gauge:

```text
Landau gauge: A = (0, Bx, 0)
t_x((x, y) -> (x+1, y)) = -1
t_y((x, y) -> (x, y+1)) = -exp(i * 2*pi * alpha * x)
```

Gauge-control implementation:

```text
Symmetric gauge: A = (-By/2, Bx/2, 0)
t_x((x, y) -> (x+1, y)) = -exp(-i * pi * alpha * y)
t_y((x, y) -> (x, y+1)) = -exp(i * pi * alpha * x)
```

Both gauges must produce Hermitian Hamiltonians. Landau gauge is used for the
primary ranking outputs; symmetric gauge is used for gauge-invariance checks.

## Numerical Tolerances

- Alpha=0 spectrum reproduction:
  `max_k |E_k^magnetic(alpha=0) - E_k^zero_field| < 1e-10` for `k = 0..5`.
- Hermiticity: `max |H - H^\dagger| < 1e-12`.
- Eigenvalue imaginary parts: `max_k |Im(E_k)| < 1e-10`.
- Gauge invariance:
  `max_k |E_k^Landau - E_k^symmetric| < 1e-6` for `k = 0..5`.

If any required numerical check fails, the sprint verdict is
`KILLED_NUMERICAL`.

## Geometry Set

Only the existing superellipse generator is used.

Primary sizes:

```text
a = {30, 36}
```

Shapes:

```text
1. n=2.0, rAR=1.0  circle baseline / symmetry baseline
2. n=2.0, rAR=0.67 ellipse / aspect-ratio baseline
3. n=1.2, rAR=1.0  diamond-like baseline
4. n=4.0, rAR=1.0  square-like / squircle baseline
```

No fifth exploratory shape is included in this sprint.

## Flux Grid

Primary weak-field grid:

```text
alpha = {0.0, 0.00125, 0.0025, 0.005}
```

Diagnostic stronger-field grid:

```text
alpha = {0.01, 0.02, 0.04}
```

The diagnostic stronger-field values cannot support `INTERESTING` or
`PROMISING` verdicts by themselves.

## Metrics

For each primary Landau-gauge spectrum:

- `E0..E5`
- `dE1 = E1 - E0`
- `dE2 = E2 - E1`
- `dE3 = E3 - E2`
- `dE4 = E4 - E3`
- `dE5 = E5 - E4`
- `min_gap_low = min(dE1, dE2, dE3)`

Do not use `Q = dE1 / (E0 + 4)` as a primary finite-field metric.

## Crossover Definition

For each size `a`:

```text
delta_crossover(a) = max(0.001, 0.01 * dE1_circle_at_alpha0_for_this_a)
```

A pairwise ranking crossover between shapes A and B counts as real only if:

1. At `alpha = 0`, `|dE1_A(0) - dE1_B(0)| > delta_crossover(a)`.
2. At some weak-field `alpha > 0`, the ranking reverses and
   `|dE1_A(alpha) - dE1_B(alpha)| > delta_crossover(a)`.
3. The crossover is not only present at alpha values with `l_B < 5`.
4. The crossover is not driven only by circular degeneracy lifting.
5. To mark `INTERESTING`, the same qualitative crossover appears for both
   `a = 30` and `a = 36`.

If a crossover appears at `a = 30` but disappears at `a = 36`, the verdict is
`KILLED_SIZE_ARTIFACT`.

## Robustness-Divergence Definition

If two shapes A and B have nearly equal zero-field gaps:

```text
|dE1_A(0) - dE1_B(0)| <= delta_crossover(a)
```

but separate under weak magnetic field:

```text
|dE1_A(alpha) - dE1_B(alpha)| > delta_crossover(a), alpha <= 0.005
```

then flag `ROBUSTNESS_DIVERGENCE_CANDIDATE`.

This is not a ranking crossover. It is a weaker signal: magnetic field breaks a
near-tie asymmetrically. It can justify a later sprint only if it survives both
sizes, is not a circle degeneracy-lifting artifact, and shows monotonic or
stable onset across nearby alpha values.

## l_B and Total Flux Diagnostics

For each alpha:

```text
l_B = 1 / sqrt(2*pi*alpha)
```

with `l_B = infinity` for `alpha = 0`. Store `l_B_over_a = l_B / a`.

For every geometry and alpha, store:

- `N_plaquettes_inside_dot`, counted from plaquettes whose four corner sites are
  present.
- `phi_total = alpha * N_plaquettes_inside_dot`.
- `phi_total_area_proxy = alpha * pi * a * b`, where `b = a * rAR`.

These are interpretation diagnostics only and do not redefine `alpha`.

Any crossover occurring only where `l_B < 5` is flagged
`STRONG_FIELD_LATTICE_ARTIFACT_CANDIDATE`.

## Killer Baselines

Compare against:

1. circle baseline: `n=2.0, rAR=1.0`
2. ellipse/aspect-ratio baseline: `n=2.0, rAR=0.67`
3. best zero-field geometry carried across alpha
4. n-only explanation
5. rAR/aspect-ratio-only explanation
6. symmetry-lifting baseline: circular `E1/E2` degeneracy splitting under
   magnetic field

A result is interesting only if there is a thresholded, weak-field, size-stable
ranking crossover or robustness divergence not explained by these baselines.

## Failure Conditions

- Numerical checks fail.
- No thresholded ranking crossover and no robustness-divergence candidate.
- Apparent effects are explained by circle, ellipse, aspect-ratio, or
  symmetry-lifting baselines.
- Effects occur only where `l_B < 5`.
- Effects appear only at `alpha = 0.005` without monotonic or stable onset.
- Effects appear at `a = 30` but disappear at `a = 36`.

## Output Files

Output directory:

```text
reports/magnetic_ranking_crossover/
```

Files:

- `sprint_plan.md`
- `magnetic_spectra.csv`
- `gauge_invariance_check.csv`
- `gap_rankings_by_alpha.csv`
- `ranking_crossovers.csv`
- `robustness_divergence.csv`
- `magnetic_response_summary.csv`
- `symmetry_artifact_diagnostics.csv`
- `baseline_comparison.csv`
- `sanity_checks.md`
- `summary.md`

No `audit.md` is produced automatically.

## Final Verdict Categories

Use exactly one verdict:

- `KILLED_NUMERICAL`
- `KILLED_NO_SIGNAL`
- `KILLED_BASELINE`
- `KILLED_STRONG_FIELD_ARTIFACT`
- `KILLED_ONSET_ARTIFACT`
- `KILLED_SIZE_ARTIFACT`
- `INTERESTING`
- `INTERESTING_WEAK`
- `PROMISING`

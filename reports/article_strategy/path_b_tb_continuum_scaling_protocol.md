# Article Path B Protocol v2:
# Superellipse-dependent TB-to-continuum convergence structure

## Current Status

This direction is not considered a positive article result yet.

Status:

HOLD -> SPRINT only after protocol review.

The only allowed first executable step is:

BESSEL_ANCHOR_ONLY.

No full superellipse comparison is allowed before the Bessel anchor passes.

This protocol exists to determine whether Path B deserves a pilot, not to
justify the result in advance.

## Purpose

This protocol defines a new positive-physics search direction for a scientific
article.

The goal is not to rescue Q/S, not to rescue magnetic ranking, and not to
demonstrate ML advantage.

The goal is to test whether low-energy tight-binding spectra of superellipse
quantum dots contain a nontrivial superellipse-exponent-dependent finite-lattice
convergence structure after removing standard continuum, Weyl, perimeter,
pixelation, and discretization baselines.

## Current Project Constraints

Closed negative lines must not be reused as positive leads:

- Q inverse screening: CLOSED NEGATIVE.
- S objective: CLOSED NEGATIVE.
- Magnetic ranking crossover: CLOSED / KILLED_BASELINE.
- ML advantage over physics baselines: NOT DEMONSTRATED.

These lines may be cited only as motivation for a baseline-first workflow.

## Core Narrow Hypothesis

For superellipse domains

```text
|x/a|^n + |y/b|^n <= 1,    b = a * rAR,
```

the low-energy tight-binding kinetic spectrum

```text
E_kin,k(a,n,rAR) = E_k(a,n,rAR) + 4
```

has a leading continuum-like term proportional to `1/a^2`.

That leading term is not the target.

The target is the residual convergence structure after subtracting the strongest
feasible baselines.

Article-relevant hypothesis:

The finite-lattice convergence residual has an exponent or structure `p(n)`
that depends systematically on the superellipse exponent `n`, survives
Weyl/perimeter/pixelation/discretization baselines, and has a falsifiable
geometric interpretation.

## Forbidden Weak Claims

Do not claim novelty from:

- `E_kin` scaling as `1/a^2`;
- Weyl area/perimeter corrections;
- generic finite-difference or lattice discretization error;
- generic "boundary shape affects spectrum";
- generic staircase-boundary error;
- corner/cusp effects unless quantified beyond simple pixelation and perimeter
  baselines;
- ML prediction accuracy;
- largest-a TB extrapolation alone.

## Physical Mechanism Hypothesis

Before running computations, test this falsifiable mechanism:

1. `n < 2`:
   Superellipse boundaries have cusp-like / high-curvature axial regions. A
   square lattice approximation should produce stronger boundary pixelation and
   anomalous boundary-site contributions.
   Expected result:
   slower convergence or larger residual amplitude after baseline subtraction.

2. `n = 2`:
   Circle/ellipse baseline. Smooth boundary. For `rAR=1.0`, exact Bessel-zero
   continuum reference exists.
   Expected result:
   cleanest convergence and strongest sanity anchor.

3. `n > 2`:
   Boundary becomes squircle-like with flatter side regions and sharper
   transition zones.
   Expected result:
   convergence differs from `n=2`, but must not be explainable only by perimeter
   or simple pixelation proxy.

Falsifiable prediction:

`p(n)` or residual amplitude should show a systematic difference between
`n=1.2`, `n=2.0`, and `n=4.0`.

A monotonic n-only fit is not enough. A pixelation-only explanation kills the
direction.

## Gate 0: Protocol Review

Before any computation, confirm that:

- `a=96` is mandatory;
- Bessel anchor is first;
- continuum reference is mandatory before INTERESTING;
- pixelation baseline is explicitly defined;
- no thesis/diploma files are modified;
- no Q/S files are modified;
- no magnetic-ranking files are modified;
- no preregistration files are modified.

If any of these are missing, do not execute.

## Mandatory Pilot Geometry Set

Pilot is not optional and must include `a=96`.

Primary pilot:

```text
rAR = 1.0
```

`n` values:

- `n = 1.2`
- `n = 2.0`
- `n = 4.0`

sizes:

- `a = 24`
- `a = 30`
- `a = 36`
- `a = 48`
- `a = 60`
- `a = 72`
- `a = 96`

Optional after pilot success only:

- `a = 120`
- `a = 144`
- `n = 3.0`
- `rAR = 0.67`
- `rAR = 0.83`
- `rAR = 1.0` expanded grid

No expansion is allowed before the pilot summary is reviewed.

## Mandatory First Execution Step

Before the full pilot, run only the Bessel anchor test.

Bessel anchor test:

Geometry:

```text
n = 2.0
rAR = 1.0
```

sizes:

```text
a = {24, 30, 36, 48, 60, 72, 96}
```

Compute:

- TB `E0..E5`
- `E_kin,k = E_k + 4`
- exact continuum circle references from Bessel zeros:
  `lambda_k / a^2`

Fit:

```text
R_k(a) = E_kin,k^TB(a) - lambda_k/a^2
```

Check:

- whether `R_k(a)` follows a stable power law;
- whether fitted exponent is stable under leave-one-size-out;
- whether residual magnitude decreases with `a`;
- whether levels with continuum degeneracy are handled correctly.

If the Bessel anchor is unstable, stop before shape comparison.

## Continuum Reference Requirement

Largest-a TB is not a sufficient continuum reference.

Allowed only as auxiliary:

Option A:
largest-a TB empirical proxy.

Mandatory before any INTERESTING or PROMISING claim:

Option B or D.

Option B:
finite-difference Dirichlet Laplacian on a finer grid for the same continuum
superellipse domain.

Option D:
high-resolution numerical Dirichlet Laplacian reference.

Circle `n=2`, `rAR=1` Bessel zeros are mandatory sanity anchors but do not
replace the general continuum reference for `n != 2`.

## Observables

For each geometry compute:

- `E0..E5`
- `E_kin,k = E_k + 4`
- scaled levels: `a^2 * E_kin,k`
- `dE1`, `dE2`, `dE3`
- scaled gaps: `a^2 * dE_j`
- `N_sites`
- continuum area proxy
- continuum perimeter proxy
- boundary-site count
- boundary pixelation proxy
- lattice-point area error
- symmetry indicators
- cusp / high-curvature proxy if implemented

Primary observables:

- `E_kin,0`
- `E_kin,1`
- `dE1`

Secondary diagnostics:

- `E_kin,2`
- `dE2`
- `dE3`

Do not use Q or S as primary objectives.

## Boundary Pixelation Proxy

Define boundary pixelation explicitly.

Required quantities:

`N_boundary_sites`:
number of lattice sites in the dot with at least one nearest neighbor outside
the dot.

`P_continuum`:
continuum perimeter of the superellipse in lattice units.

Because lattice spacing is one, expected boundary count scales as
`P_continuum`, not `P_continuum/a`.

Define:

```text
boundary_pixelation_proxy =
abs(N_boundary_sites - c * P_continuum) / P_continuum
```

where `c` is either:

- fixed to `1` as a first diagnostic, or
- fitted globally as a nuisance scale factor across all pilot geometries.

Also compute:

```text
area_pixelation_proxy =
abs(N_sites - A_continuum) / A_continuum
```

where `A_continuum` is the continuum area in lattice-site units.

If the residual is explained by `boundary_pixelation_proxy` or
`area_pixelation_proxy`, the direction is killed.

## Baseline Ladder

Every candidate residual must be compared against:

1. leading continuum-like `1/a^2` confinement;
2. exact Bessel anchor for circle;
3. area / `N_sites` correction;
4. perimeter correction;
5. aspect-ratio correction;
6. Weyl-type area/perimeter baseline;
7. lattice-point area error;
8. boundary pixelation proxy;
9. cusp / high-curvature proxy;
10. n-only monotonic baseline;
11. rAR-only baseline;
12. continuum or dense-grid Dirichlet reference.

If any simple baseline explains the residual, the direction is killed.

## Residual Definitions

Define:

`R1`:
`E_kin,k(a,n,rAR) - C_k(n,rAR)/a^2`

`R2`:
`a^2 * E_kin,k(a,n,rAR) - C_k(n,rAR)`

`R3`:
residual after fitting a baseline model using:

- `1/a^2`
- area proxy
- perimeter proxy
- `N_sites`
- boundary pixelation proxy
- area pixelation proxy
- `n`
- `rAR`

Only `R3` or a stronger residual is article-relevant.

`R1` and `R2` are diagnostics only.

## Candidate Scaling Fits

For each fixed `n` and `rAR`, fit:

```text
R(a) ~ c * a^(-p)
```

Compare:

- fixed `p` across all `n`;
- `p` depending only on boundary pixelation proxy;
- `p` depending only on area pixelation proxy;
- `p` depending only on perimeter/area;
- `p` depending only on cusp/high-curvature proxy;
- unconstrained `p(n)`.

Use AIC/BIC or cross-validated error only as secondary evidence.

Main evidence must be:

- stability under leave-one-size-out;
- physical interpretability;
- consistency with continuum reference.

## Kill Conditions

Verdict `KILLED_BASELINE` if:

- residual is explained by area/perimeter/`N_sites`/aspect-ratio baseline;
- residual is explained by `boundary_pixelation_proxy`;
- residual is explained by `area_pixelation_proxy`;
- `R3` correlates with `boundary_pixelation_proxy` with `R^2 > 0.8` across
  pilot geometries;
- `p(n)` is not stable under removing one size point;
- `p(n)` disappears when `a=96` is included;
- signal exists only for `n=1.2` and is explainable by cusp/high-curvature
  proxy;
- signal is comparable to numerical solver tolerance;
- continuum/dense-grid reference contradicts the trend.

Verdict `KILLED_BESSEL_ANCHOR` if:

- circle `n=2`, `rAR=1` Bessel anchor fails;
- TB-to-Bessel residual is not stable enough to define a scaling test;
- degeneracy handling for circle levels is inconsistent.

Verdict `KILLED_NUMERICAL` if:

- spectra are not stable;
- low eigenvalues are not sorted/finite;
- Hamiltonian checks fail;
- scaling is dominated by solver/extraction artifacts.

Verdict `KILLED_TRIVIAL` if:

- the only observed behavior is `1/a^2` confinement;
- the result is just Weyl/perimeter correction;
- the result is generic finite-difference convergence;
- the result is generic staircase-boundary error.

## Interesting Conditions

Verdict `INTERESTING` only if:

- Bessel anchor passes;
- continuum or dense-grid reference exists;
- after subtracting strong baselines, a systematic residual remains;
- residual structure is stable when `a=96` is included;
- residual structure is stable under leave-one-size-out;
- effect differs between `n=1.2`, `n=2.0`, and `n=4.0`;
- effect is not explained by area/perimeter/`N_sites`/pixelation;
- direct Kwant spectra support the effect before any ML is used.

Verdict `PROMISING` only if:

- residual structure survives expanded `n` and `rAR` grid;
- residual/convergence exponent has a clear physical interpretation;
- continuum/dense-grid reference supports the same trend;
- the effect can be summarized in one figure and one equation.

## No ML Rule

No ML in this sprint.

ML may be considered only after a direct non-baseline residual is found.

## Required Future Execution Outputs

If this protocol is later executed, outputs must go to:

```text
reports/article_path_b_tb_continuum_scaling/
```

Expected future files:

- `bessel_anchor_spectra.csv`
- `bessel_anchor_fit.csv`
- `scaling_spectra.csv`
- `scaled_levels_by_size.csv`
- `continuum_reference_checks.csv`
- `pixelation_proxies.csv`
- `residual_baseline_comparison.csv`
- `convergence_exponent_fits.csv`
- `kill_tests.md`
- `summary.md`

But this protocol task must not generate these files yet.

## First Post-Protocol Sprint

After protocol review, the first executable sprint is:

BESSEL_ANCHOR_ONLY

It must compute only the circle `n=2`, `rAR=1`,
`a={24,30,36,48,60,72,96}`.

No shape comparison is allowed until Bessel anchor passes.

# Magnetic Ranking-Crossover Closure

## Status

CLOSED / KILLED_BASELINE

## Tested Hypothesis

Weak perpendicular magnetic flux might induce geometry-dependent low-energy
ranking crossovers or robustness divergences in superellipse tight-binding
dots.

## Protocol Summary

- Direct Kwant only.
- No ML.
- No inverse screening.
- Shapes tested:
  - `n=2.0, rAR=1.0`: circle / symmetry baseline.
  - `n=2.0, rAR=0.67`: ellipse / aspect-ratio baseline.
  - `n=1.2, rAR=1.0`: diamond-like baseline.
  - `n=4.0, rAR=1.0`: square-like / squircle baseline.
- Sizes: `a = {30, 36}`.
- Weak-field alpha grid: `{0.0, 0.00125, 0.0025, 0.005}`.
- Diagnostic alpha grid: `{0.01, 0.02, 0.04}`.

## Numerical Status

- Alpha=0 reproduction passed.
- Gauge invariance passed.
- Hermiticity passed.
- Eigenvalue imaginary-part check passed.
- Finite sorted spectra passed.

## Result

- No thresholded ranking crossovers were found.
- Robustness-divergence candidates did not survive filters.
- Observed candidates are explained by the circle/ellipse symmetry baseline.

## Interpretation

Magnetic field response exists numerically, but in this tested family it does
not produce a non-baseline geometry-dependent design signal.

## Explicit Warning

This sprint must not be used as a positive magnetic inverse-design result. Do
not expand this branch as a rescue attempt. Any future magnetic work requires a
new protocol excluding circle-driven degeneracy effects from the primary signal
definition.

## Recommended Project-Level Status

- Q/S inverse screening: closed negative.
- S objective: closed negative.
- Magnetic ranking crossover: closed negative.
- ML advantage over physics baselines: not demonstrated.

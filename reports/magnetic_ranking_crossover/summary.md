# Magnetic Ranking-Crossover Sprint Summary

Final verdict: `KILLED_BASELINE`

Verdict reason: All thresholded signals were explained by the circle symmetry-lifting baseline.

## Scope

This was an exploratory direct-Kwant falsification sprint. It was not an ML
task, not inverse screening, and not a rescue run for the closed Q/S line.

- Geometries: circle_n2_r1 (n=2.0, rAR=1.0), ellipse_n2_r067 (n=2.0, rAR=0.67), diamond_n12_r1 (n=1.2, rAR=1.0), squircle_n4_r1 (n=4.0, rAR=1.0)
- Sizes: `a = {30, 36}`
- Weak-field alpha grid: `(0.0, 0.00125, 0.0025, 0.005)`
- Diagnostic alpha grid: `(0.01, 0.02, 0.04)`
- All alpha values computed: `(0.0, 0.00125, 0.0025, 0.005, 0.01, 0.02, 0.04)`

## Numerical Status

- alpha=0 reproduced zero-field spectra: `True`
- gauge invariance passed: `True`
- maximum gauge difference: `1.865174681370263e-14`
- Hamiltonian Hermiticity passed: `True`
- eigenvalue imaginary-part check passed: `True`
- finite sorted spectra passed: `True`

## Field Diagnostics

- l_B filter status: all weak-field alpha values pass l_B >= 5; diagnostic alpha values below cutoff are not eligible for primary claims
- phi_total range: `0.0` to `184.64000000000001`

## Signal Diagnostics

- thresholded pairwise ranking crossovers: `0`
- crossovers surviving pre-size filters: `0`
- robustness-divergence candidates: `3`
- robustness divergences surviving pre-size filters: `0`

The strongest baseline remains the fixed zero-field geometry/aspect-ratio
ranking unless a thresholded weak-field signal survives the explicit killer
baseline filters and both sizes.

No Q/S final outputs, preregistration files, or thesis files are modified by
this sprint.

# Bessel Anchor Summary

## Protocol Status

This is the Article Path B `BESSEL_ANCHOR_ONLY` sprint. It does not run
the full Path B pilot, does not compare superellipse exponents, does not
use ML, and does not use Q or S objectives.

## Tested Geometry

- n: `2.0`
- rAR: `1.0`
- shape: circular superellipse anchor
- sizes: `(24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0)`

## Bessel Reference Definition

Continuum Dirichlet disk eigenvalues are

```text
lambda_{m,s} = j_{m,s}^2 / a^2
```

with non-degenerate `m=0` levels and twofold-degenerate `m>0` levels.
The first six continuum disk levels, including degeneracies, were used.

## Degeneracy Handling

- degeneracy reported: `True`
- groups: `{'m0_s1': 1, 'm0_s2': 1, 'm1_s1': 2, 'm2_s1': 2}`
- max TB splitting by degenerate group: `{'m1_s1': 2.0161650127192843e-13, 'm2_s1': 0.00018957319238444015}`

Individual residuals and group-averaged residual fits are both reported.

## Numerical Sanity Checks

- spectra finite and sorted: `True`
- E_kin positive: `True`
- E_kin decreases with a: `True`
- scaled values approach Bessel lambdas: `True`

## Tables Summary

- `bessel_anchor_spectra.csv` stores individual TB levels, Bessel references, residuals, scaled values, and degeneracy groups.
- `bessel_anchor_fit.csv` stores individual-level and group-averaged residual power-law fits.
- No plots were generated; tables are sufficient for this sprint.

## Residual Magnitude Decrease

- level_0: |R(a=96)| / |R(a=24)| = `0.0186853`
- level_1: |R(a=96)| / |R(a=24)| = `0.0180589`
- level_2: |R(a=96)| / |R(a=24)| = `0.0180589`
- level_3: |R(a=96)| / |R(a=24)| = `0.0172373`
- level_4: |R(a=96)| / |R(a=24)| = `0.0173844`
- level_5: |R(a=96)| / |R(a=24)| = `0.0170714`

## Power-Law Fit Stability

- level_0: p=`2.96103`, LOO p range=`2.90376`..`3.0394`, verdict=`passed`
- level_1: p=`2.98312`, LOO p range=`2.92761`..`3.0564`, verdict=`passed`
- level_2: p=`2.98312`, LOO p range=`2.92761`..`3.0564`, verdict=`passed`
- level_3: p=`3.04535`, LOO p range=`2.96079`..`3.15648`, verdict=`passed`
- level_4: p=`2.96929`, LOO p range=`2.93436`..`3.01095`, verdict=`passed`
- level_5: p=`3.01986`, LOO p range=`2.96698`..`3.08531`, verdict=`passed`
- group_m0_s1: p=`2.96103`, LOO p range=`2.90376`..`3.0394`, verdict=`passed`
- group_m0_s2: p=`3.01986`, LOO p range=`2.96698`..`3.08531`, verdict=`passed`
- group_m1_s1: p=`2.98312`, LOO p range=`2.92761`..`3.0564`, verdict=`passed`
- group_m2_s1: p=`3.01027`, LOO p range=`2.95728`..`3.07712`, verdict=`passed`

## Final Verdict

`BESSEL_ANCHOR_PASSED`

Reasons:

- Ground and main low-level residual fits were stable and decreasing.

This verdict applies only to the circle Bessel anchor. It is not a positive
Path B article result and does not authorize full shape comparison by itself.

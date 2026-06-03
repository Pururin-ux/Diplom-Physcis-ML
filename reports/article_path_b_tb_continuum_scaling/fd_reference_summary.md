# FD Continuum Reference Summary

## Scope

This is the Article Path B FD-reference-only step. It implements and
validates a finite-difference Dirichlet Laplacian continuum reference.
It does not validate Path B, does not run tight-binding spectra, does not
run shape contrast, does not fit an effective radius, does not use ML,
and does not use Q or S objectives.

## FD Method

- Unit-scaled superellipse domain: `|X|^n + |Y/rAR|^n < 1`.
- `rAR = 1.0` for this step.
- Uniform Cartesian grid on `[-1, 1] x [-1, 1]`.
- Strict interior points are unknowns; outside and boundary points impose
  Dirichlet zero values.
- Positive 5-point finite-difference Laplacian `-Delta`.
- Lowest six eigenvalues computed with sparse `eigsh`.

## Grid Resolutions

- N_grid values: `(101, 151, 201, 251)`
- n values: `(1.2, 2.0, 4.0)`

## Bessel Validation for n=2 Circle

| N_grid | level | lambda_fd_unit | lambda_bessel | rel_error | group |
|---:|---:|---:|---:|---:|---|
| 101 | 0 | 5.717858858 | 5.783185963 | 0.011296 | m0_s1 |
| 101 | 1 | 14.51285783 | 14.68197064 | 0.0115184 | m1_s1 |
| 101 | 2 | 14.51285783 | 14.68197064 | 0.0115184 | m1_s1 |
| 101 | 3 | 26.04844855 | 26.37461643 | 0.0123667 | m2_s1 |
| 101 | 4 | 26.07782136 | 26.37461643 | 0.0112531 | m2_s1 |
| 101 | 5 | 30.10824791 | 30.47126234 | 0.0119133 | m0_s2 |
| 151 | 0 | 5.734380039 | 5.783185963 | 0.00843928 | m0_s1 |
| 151 | 1 | 14.55570707 | 14.68197064 | 0.00859991 | m1_s1 |
| 151 | 2 | 14.55750542 | 14.68197064 | 0.00847742 | m1_s1 |
| 151 | 3 | 26.1391705 | 26.37461643 | 0.00892699 | m2_s1 |
| 151 | 4 | 26.15275504 | 26.37461643 | 0.00841193 | m2_s1 |
| 151 | 5 | 30.20571101 | 30.47126234 | 0.00871481 | m0_s2 |
| 201 | 0 | 5.743903124 | 5.783185963 | 0.00679259 | m0_s1 |
| 201 | 1 | 14.58142306 | 14.68197064 | 0.00684837 | m1_s1 |
| 201 | 2 | 14.58142306 | 14.68197064 | 0.00684837 | m1_s1 |
| 201 | 3 | 26.18926479 | 26.37461643 | 0.00702765 | m2_s1 |
| 201 | 4 | 26.19485414 | 26.37461643 | 0.00681573 | m2_s1 |
| 201 | 5 | 30.25956839 | 30.47126234 | 0.00694733 | m0_s2 |
| 251 | 0 | 5.752993834 | 5.783185963 | 0.00522067 | m0_s1 |
| 251 | 1 | 14.60479632 | 14.68197064 | 0.0052564 | m1_s1 |
| 251 | 2 | 14.60479638 | 14.68197064 | 0.0052564 | m1_s1 |
| 251 | 3 | 26.23141362 | 26.37461643 | 0.00542957 | m2_s1 |
| 251 | 4 | 26.23807062 | 26.37461643 | 0.00517717 | m2_s1 |
| 251 | 5 | 30.30916245 | 30.47126234 | 0.00531976 | m0_s2 |

At the selected highest grid:

- selected N_grid: `251`
- ground-state relative error: `0.0052206740942014095`
- max low-level relative error: `0.0054295692303389775`
- max low-level absolute error: `0.16209989420846682`

## Degeneracy Handling

Individual FD levels are reported. Degenerate Bessel groups are labeled for
the circle, and splitting is reported rather than hidden.

- selected-grid Bessel-group splitting: `{'m1_s1': 6.129738139293295e-08, 'm2_s1': 0.006657003025711816}`

## Final Chosen Reference Values

| n | level | N_grid | h | lambda_fd_unit | group |
|---:|---:|---:|---:|---:|---|
| 1.2 | 0 | 251 | 0.008 | 8.010106083 |  |
| 1.2 | 1 | 251 | 0.008 | 20.14943153 |  |
| 1.2 | 2 | 251 | 0.008 | 20.14943153 |  |
| 1.2 | 3 | 251 | 0.008 | 33.13996729 |  |
| 1.2 | 4 | 251 | 0.008 | 39.34050534 |  |
| 1.2 | 5 | 251 | 0.008 | 40.93499173 |  |
| 2.0 | 0 | 251 | 0.008 | 5.752993834 | m0_s1 |
| 2.0 | 1 | 251 | 0.008 | 14.60479632 | m1_s1 |
| 2.0 | 2 | 251 | 0.008 | 14.60479638 | m1_s1 |
| 2.0 | 3 | 251 | 0.008 | 26.23141362 | m2_s1 |
| 2.0 | 4 | 251 | 0.008 | 26.23807062 | m2_s1 |
| 2.0 | 5 | 251 | 0.008 | 30.30916245 | m0_s2 |
| 4.0 | 0 | 251 | 0.008 | 5.040779685 |  |
| 4.0 | 1 | 251 | 0.008 | 12.68636268 |  |
| 4.0 | 2 | 251 | 0.008 | 12.68636268 |  |
| 4.0 | 3 | 251 | 0.008 | 20.91294157 |  |
| 4.0 | 4 | 251 | 0.008 | 24.74317846 |  |
| 4.0 | 5 | 251 | 0.008 | 25.82400856 |  |

## Stability Across Two Finest Grids

- max relative level change by n: `{1.2: 0.002171264522746753, 2.0: 0.00164709096579452, 4.0: 0.0011635349829582392}`

## Limitations

- This is a finite-difference reference on embedded Cartesian masks, not an
  analytic continuum solution for `n != 2`.
- The reference is not yet compared against tight-binding residuals.
- This step does not establish n-dependent finite-lattice structure.
- Degenerate continuum levels can be split by grid anisotropy; both levels
  must remain visible in downstream analysis.

## Effective-Radius Baseline Warning

The next executable shape-contrast step must test:

```text
E_kin,0(a,n) = lambda_ref_0(n) / (a + delta_n)^2
```

and compute:

```text
R_eff(a,n) = E_kin,0(a,n) - lambda_ref_0(n)/(a + delta_n)^2
```

Path B must be killed as `KILLED_EFFECTIVE_RADIUS_BASELINE` if:

- the effective-radius fit explains the TB spectra for all tested n;
- `delta_n` is stable across a;
- `delta_n` is predicted by perimeter, `N_boundary`, area pixelation, or
  boundary pixelation proxy;
- `R_eff` has no remaining systematic n-dependent structure.

## Final Verdict

`FD_REFERENCE_VALIDATION_PASSED`

Reasons:

- Circle ground-state relative error at selected grid is 0.00522067.
- Non-circle reference values are finite, sorted, and stable across the two finest grids.
- Degeneracy splitting is reported rather than hidden.

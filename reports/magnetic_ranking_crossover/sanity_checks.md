# Magnetic Sprint Sanity Checks

This file records numerical checks only. It is not a scientific result by itself.

## Required Checks

- alpha0_reproduction_passed: `True`
- max_alpha0_reproduction_error: `4.263256414560601e-14`
- alpha0_tolerance: `1e-10`
- hermiticity_passed: `True`
- max_hermiticity_error: `0.0`
- hermiticity_tolerance: `1e-12`
- eigen_imag_passed: `True`
- max_eigen_imag: `0.0`
- eigen_imag_tolerance: `1e-10`
- gauge_invariance_passed: `True`
- max_gauge_invariance_error: `1.865174681370263e-14`
- gauge_tolerance: `1e-06`
- finite_sorted_passed: `True`
- numerical_passed: `True`

## Field Diagnostics

- l_B_filter_status: all weak-field alpha values pass l_B >= 5; diagnostic alpha values below cutoff are not eligible for primary claims
- phi_total_min: `0.0`
- phi_total_max: `184.64000000000001`

If any required numerical check fails, the sprint verdict must be `KILLED_NUMERICAL`.

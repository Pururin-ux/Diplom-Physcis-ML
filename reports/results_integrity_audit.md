# Results integrity audit

## Executive verdict

The validation cleanup does not change the thesis numerical conclusions. The fixed
superellipse eigensolver path reproduces the saved dense dataset within tight
floating-point tolerance. No dataset overwrite is required.

## Issue

`src/dataset.py::_superellipse_levels_and_site_count` called
`scipy.sparse.linalg.eigsh` directly and then sorted/cast the eigenvalues inline.
This bypassed the shared `_as_sorted_real_finite` validation helper used by the
rectangular spectrum path in `src/kwant_solver.py`. The issue was a validation and
DRY inconsistency in the primary superellipse dataset-generation path.

## Severity

2 = secondary/validation safety issue.

The raw spectra and geometry extraction are unchanged within numerical roundoff,
but the primary superellipse path now uses the same real/finite validation policy
as the shared solver helper.

## Code fix

`src/dataset.py` now imports `_as_sorted_real_finite` from `src.kwant_solver`.
After `eigvalsh` or `eigsh` computes the candidate eigenvalues,
`_superellipse_levels_and_site_count` calls `_as_sorted_real_finite(vals)` before
checking that exactly four energies were returned.

No physics, geometry, model features, or dataset schema were changed.

## Dataset equivalence check

- Dataset file compared: `data/superellipse_discrete_n_dense_dataset.npz`
- Grid size: 140 geometries
- Grid:
  - `a = [24, 27, 30, 33, 36]`
  - `aspect_ratio = [0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0]`
  - `n = [1.2, 2.0, 3.0, 4.0]`

Compared arrays:

- Geometry/site arrays: `a`, `b`, `aspect_ratio`, `n`, `N_sites`
- Energy arrays: `E0`, `E1`, `E2`, `E3`
- Gap arrays: `dE1`, `dE2`, `dE3`

Results:

- Maximum absolute difference for `E0`-`E3`: `1.127986593019159e-13`
- Maximum absolute difference for `dE1`-`dE3`: `1.2878587085651816e-13`
- `N_sites` identical: yes
- Geometry arrays identical: yes
- All compared arrays equal within `rtol=0`, `atol=1e-12`: yes

Conclusion: the fixed code reproduces the saved dense dataset within numerical
roundoff from the sparse eigensolver. No official dataset regeneration is needed.

## Tests

Command:

```text
conda run -n diplom-kwant python -m pytest tests -q
```

Result:

```text
34 passed, 1 warning
```

The warning is the pre-existing OpenMP/threadpool warning.

## Required downstream action

No notebooks, reports, thesis tables, or thesis conclusions need to be rerun or
rewritten for this validation cleanup. The saved dense dataset is equivalent to
the regenerated fixed-code output within `1e-12` absolute tolerance.

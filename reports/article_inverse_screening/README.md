# Article inverse screening report

This report tests one-shot surrogate-guided inverse spectral screening.
It is not closed-loop inverse design because no iterative retraining loop is used.

The surrogate Ridge models generate candidates only. Final candidate and
baseline values in `main_candidates_verified.csv` are direct Kwant
calculations or already Kwant-computed training rows.

Continuous parameters `(a, aspect_ratio)` induce discrete Kwant lattice
domains, so candidate geometries are deduplicated by a stable hash of
integer site coordinates.

## How to rerun

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python scripts\run_article_inverse_screening.py
```

## Summary

- n=1.2: selected=5, best_Q=1.5160295869298364, success=False. LOAO/LOARO Ridge error scale loaded; no_root=0; duplicate_training=0; duplicate_candidate=14
- n=2.0: selected=5, best_Q=1.5367475903713435, success=False. LOAO/LOARO Ridge error scale loaded; no_root=0; duplicate_training=0; duplicate_candidate=7
- n=3.0: selected=5, best_Q=1.525527776256471, success=False. LOAO/LOARO Ridge error scale loaded; no_root=0; duplicate_training=0; duplicate_candidate=2
- n=4.0: selected=5, best_Q=1.514312730907552, success=False. LOAO/LOARO Ridge error scale loaded; no_root=0; duplicate_training=0; duplicate_candidate=6

## Limitations

- The search is restricted to the verified training-domain ranges.
- Surrogate roots are off-grid candidate proposals, not physical truth.
- The reported success criterion is conservative and first-pass.
- No thesis chapter or thesis conclusion is modified by this report.

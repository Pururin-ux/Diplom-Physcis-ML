# TB Self-Scaling Gate Summary

## Scope

This is a TB-only self-consistent finite-size scaling gate for Article
Path B after the embedded-mask FD reference failed the N501 convergence
gate. It uses direct tight-binding ground-state values and geometric
diagnostics only.

No FD reference was used. No FD reference values were loaded. No TB-vs-FD
residuals were computed. Shape contrast against FD remains blocked.

The analysis does not use ML, Q, or S objectives.

## Tested Domain

- rAR: `1.0`
- n values: `(1.2, 2.0, 4.0)`
- sizes: `(24.0, 30.0, 36.0, 48.0, 60.0, 72.0, 96.0)`
- verdict is based on the ground state only

## n=2.0 Bessel Calibration

- exact disk ground value `j01^2`: `5.783185962946783`
- effective_radius: relative error `0.0007209480542874929`
- linear_inverse_size: relative error `0.0008560935982796461`
- power_law_residual: relative error `0.009866785629341993`
- quadratic_inverse_size: relative error `0.003319699918392144`
- best n=2.0 relative error: `0.0007209480542874929`
- n=2.0 model-to-model lambda spread / Bessel: `0.01072287922762164`
- calibration accepted: `True`

## Fitted Ground-State Parameters

- effective-radius lambda_TB_inf by n: n=1.2: `8.02997104795634`, n=2.0: `5.779016586279214`, n=4.0: `5.049343349769357`
- effective-radius delta_n by n: n=1.2: `0.27906669566307835`, n=2.0: `0.27654413026109254`, n=4.0: `0.13047028456603266`
- power-law p_TB(n): n=1.2: `0.10000000000001663`, n=2.0: `0.5332825748871706`, n=4.0: `1.0516256034280165`
- power-law LOO stability accepted for all n: `False`

Important interpretation: `lambda_TB_inf(n)` depending on `n` is ordinary
shape dependence of continuum-like eigenvalues. It is not treated as a
novel Path B signal.

## Effective-Radius Baseline

- killed signal: `False`
- criterion: high per-n fit quality and no systematic residual structure
  large enough to justify downstream continuum-reference repair

## Boundary-Fraction Baseline

- R2: `1.1221410930462028e-06`
- leave-one-row-out R2: `-0.30289566099358955`
- max absolute mean residual by n after baseline: `1.6571804105988092e-06`
- killed signal: `False`

## Pixelation / Geometry Baselines

- best simple baseline: `area_pixelation_proxy`
- best simple baseline R2: `0.06594156193225253`
- best simple baseline leave-one-row-out R2: `-0.1560741465624409`
- best simple baseline max absolute mean residual by n: `0.003992071487324559`
- killed signal: `False`

Feature baseline diagnostics:

- A_continuum: R2=`0.016646913910341787`, LOO_R2=`-0.17774673727701362`
- N_boundary_sites: R2=`0.010153247819493894`, LOO_R2=`-0.2288178872866249`
- N_sites: R2=`0.01653853499689495`, LOO_R2=`-0.17761880231721006`
- P_continuum: R2=`0.01488937243810562`, LOO_R2=`-0.21638515709158157`
- area_pixelation_proxy: R2=`0.06594156193225253`, LOO_R2=`-0.1560741465624409`
- boundary_fraction: R2=`1.1221410930462028e-06`, LOO_R2=`-0.30289566099358955`
- boundary_pixelation_proxy: R2=`0.0010372176865866`, LOO_R2=`-0.32992400611167194`

## Surviving Signal

- TB self-scaling survives minimal gate: `False`

## Final Verdict

`TB_SELF_SCALING_INCONCLUSIVE`

If this verdict is killed or inconclusive, Path B should be closed or
reframed as a negative benchmark / baseline-first audit. Shortley-Weller
or cut-cell FD repair is not recommended unless the TB self-scaling signal
survives this minimal gate.

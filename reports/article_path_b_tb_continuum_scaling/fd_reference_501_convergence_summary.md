# FD N501 Convergence Gate Summary

## Scope

This is an FD-only asymptotic convergence check for the Article Path B
continuum reference. It does not run tight-binding spectra, does not run
shape contrast, does not fit an effective-radius delta, does not use ML,
and does not use Q or S objectives.

## Why N_grid=501 Was Added

The previous selected FD reference used `N_grid=251`, where the circle
ground-state FD-vs-Bessel relative error was about `0.52%`. Before using
FD references for TB residual analysis, this check adds a near-geometric
refinement triple `N_grid={126,251,501}` so observed convergence order and
reference uncertainty can be measured directly.

## Why N_grid=301 Was Not Used

`N_grid=301` does not complete the intended h-halving test around the
existing `N_grid=251` reference. The chosen `126,251,501` sequence gives
approximately `h={0.016,0.008,0.004}` and directly tests whether the
finest existing reference behaves consistently under near-geometric
refinement.

## Grid Triples

- primary refinement triple: `(126, 251, 501)`
- existing-grid consistency triple: `(151, 201, 251)`

All p estimates use the general unequal-step equation solved with
`scipy.optimize.brentq`. The simple `log2(Delta12/Delta23)` shortcut is
not used.

## Ground-State Observed Orders

- n=2.0 Bessel-error p, primary triple: `1.0713957900534805`
- n=1.2 self-convergence p, primary triple: `0.8449154922155621`
- n=4.0 self-convergence p, primary triple: `0.6960105578391392`
- n=1.2 self-convergence p, consistency triple: `1.5850789584797165`
- n=4.0 self-convergence p, consistency triple: `None`

The p estimates should be interpreted as observed numerical behavior of
the embedded-mask FD discretization. For `n=1.2`, the domain is treated
as a convex superellipse with singular/high-curvature boundary regions,
not as a reentrant-corner domain.

## Extrapolation and Reference Uncertainty

- n=2.0 raw N501 ground relative error vs Bessel: `0.0026734921480308575`
- n=1.2 level-0 reference uncertainty: `0.03796342892613502`
- n=1.2 level-0 relative reference uncertainty: `0.0047216251159203785`
- n=4.0 level-0 reference uncertainty: `0.011066304913905256`
- n=4.0 level-0 relative reference uncertainty: `0.0021923716263753637`

Hard gate:

- relative_reference_uncertainty(n=1.2, level 0) < 0.001: `False`
- relative_reference_uncertainty(n=4.0, level 0) < 0.001: `False`

## Shape-Dependent FD Error Risk

- FD_REFERENCE_SHAPE_DEPENDENT_ERROR_RISK: `True`

Risk reasons:

- p(n=1.2) is unstable between primary and consistency triples
- n=1.2 reference uncertainty is too large for downstream TB residual analysis
- n=4.0 reference uncertainty requires downstream qualification

## Recommended Reference Model

- recommended reference model: `FD_REFERENCE_INSUFFICIENT_FOR_SHAPE_CONTRAST`
- minimal shape contrast allowed next: `False`

If the verdict is not `FD_501_CONVERGENCE_PASSED`, do not run shape
contrast. Recommended alternatives are higher `N_grid`, a better boundary
treatment, an alternative continuum solver, or removing `n=1.2` as a
primary shape.

## Final Verdict

`FD_501_CONVERGENCE_INCONCLUSIVE`

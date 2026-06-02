# Direct Kwant near-isotropy sweep

This sweep was run because the previous symmetry-optimum analysis used a
surrogate-defined dense iso-Ekin curve with only representative direct
Kwant checks. Here, near isotropy, every reported point is selected by a
local direct-Kwant refinement around the surrogate iso-Ekin root.

Exact Ekin matching is not imposed because continuous superellipse
parameters induce discrete lattice domains; Ekin changes stepwise with
the selected site set. For each requested aspect ratio, the selected
geometry is the local candidate with minimum absolute Ekin error.

This is not a new inverse-design objective, and S = (E2-E1)/Ekin is not
optimized here.

## Summary

- n=1.2: status=ambiguous; Q_iso_minus_best_noniso=0.0016332209719751578; noniso_beats_iso=False.
- n=2.0: status=ambiguous; Q_iso_minus_best_noniso=0.003977721348570107; noniso_beats_iso=False.
- n=3.0: status=ambiguous; Q_iso_minus_best_noniso=-4.340972026284362e-13; noniso_beats_iso=True.
- n=4.0: status=ambiguous; Q_iso_minus_best_noniso=-0.000709622777190555; noniso_beats_iso=True.

At least one non-isotropic point has larger raw Q than isotropy, but
the report classifies gains conservatively using a 2% threshold.
Therefore the strict near-isotropy optimum claim is ambiguous, not
confirmed as a clean maximum.

The broader symmetry explanation remains plausible because Q keeps a
positive rank trend toward isotropy and S decreases toward near-zero
at isotropy, but the direct sweep does not prove a strict isotropic
maximum in the discrete lattice setting.

S remains a plausible next pre-registered objective only as a separate
new experiment with direct Kwant verification and strong baselines. This
sweep does not establish inverse-design success.

## Limitations

- The sweep is local near isotropy and does not replace a full direct Kwant
  sweep of the whole domain.
- The selected geometries minimize local Ekin error but are not exactly
  iso-Ekin matched.
- Continuous parameters can map to duplicate discrete geometries.
- Thesis files and thesis conclusions are not modified.

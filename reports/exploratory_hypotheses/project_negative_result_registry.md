# Project Negative-Result Registry

## Purpose

This registry records explored directions that were closed, killed by
baselines, or downgraded. It exists to prevent accidental reuse of negative
results as positive leads.

## Closed / Negative Lines

### Q inverse screening

Status: **CLOSED NEGATIVE**

Reason:
Q = dE1 / (E0 + 4) was biased toward isotropy and did not yield a non-baseline
inverse-design signal.

Killed by:
- isotropy baseline;
- same-n baseline;
- direct Kwant verification.

Do not reframe as:
- successful inverse design;
- ML-guided discovery.

### S objective

Status: **CLOSED NEGATIVE**

Reason:
S = (E2 - E1) / (E0 + 4) behaved as a monotonic anisotropy diagnostic.

Killed by:
- simple anisotropy baseline;
- strongest feasible physics baseline;
- direct Kwant verification.

Do not reframe as:
- nontrivial spectral design;
- surrogate discovery.

### Magnetic ranking crossover

Status: **CLOSED / KILLED_BASELINE**

Closure commit:
73f4806720413e598066761287b0b27f8257a072

Reason:
No thresholded weak-field geometry-ranking crossover survived the protocol.
Robustness-divergence candidates were explained by circle/ellipse symmetry
lifting.

Killed by:
- circle/ellipse symmetry baseline;
- zero-field/aspect-ratio ranking;
- explicit weak-field and size-stability filters.

Numerical checks:
- alpha=0 reproduction passed;
- gauge invariance passed;
- Hermiticity passed;
- eigenvalue imaginary-part check passed;
- finite sorted spectra passed.

Do not reframe as:
- positive magnetic inverse-design signal;
- magnetic robustness discovery;
- ML opportunity.

Future magnetic work:
Allowed only under a new protocol that excludes circle-driven degeneracy effects
from the primary signal definition.

### Generic lattice residual / boundary-angle line

Status: **NOT PURSUED AS ARTICLE LEAD**

Reason:
Generic finite-size / boundary corrections risk rediscovering Weyl, perimeter,
curvature, and discretization-error physics. Prior residual diagnostics already
found no universal simple boundary explanation; only a weak n=1.2 diagnostic
signal appeared.

Do not reframe as:
- Weyl correction novelty;
- boundary-angle novelty without continuum/dense-grid reference;
- lattice-residual article claim without new scaling protocol.

Future work:
Allowed only as a separate computational-physics project with:
- larger size range;
- dense-grid or continuum reference;
- explicit Weyl/perimeter/curvature baselines;
- a preregistered residual/convergence hypothesis.

## Current Project-Level Conclusion

The tested superellipse tight-binding family is dominated by simple physical
baselines for the explored low-energy spectral objectives.

ML advantage over physics-informed baselines has not been demonstrated.

Magnetic-field ranking crossover did not produce a non-baseline design signal.

The safe scientific framing is a baseline-first negative benchmark, not a
positive inverse-design claim.

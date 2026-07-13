# Effective two-level model of the doublet response

Protocol section 4. A minimal model of the (nearly) degenerate first-excited
doublet, used to identify exactly what each observable measures. Presented as a
model, then checked against the numerical data; not claimed proven beyond that.

## Model

In the 2D doublet subspace, write the effective Hamiltonian (traceless part) as
a real symmetric 2x2 matrix on the Pauli basis {sigma_z, sigma_x} (the doublet
is time-reversal symmetric, so sigma_y does not enter for real hopping):

  H_eff(p, delta) = E_c(p, delta) I + [ b(p, a) + delta * s ] . sigma,

with:
- `b(p, a)` = digital PLACEMENT anisotropy at delta=0 (a 2-vector in the
  (sigma_z, sigma_x) plane); nonzero for generic placements, zero for C4v;
- `s` = CONTINUUM shape perturbation vector (the Hadamard quadrupole); for the
  area-preserving deformation it points along the quadrupole axis with magnitude
  set by `j11^2/(2 j01^2)` in dimensionless units;
- `delta` = deformation; `p` = placement phase.

The instantaneous splitting magnitude is `2|b + delta s|`, the invariant object.

## What each observable measures

Let `hat b = b/|b|`, and let the angle between `b` and `s` be `phi_ps`.

- Sorted gap `|E2 - E1|/delta = 2|b + delta s|/delta`. For b != 0 this diverges
  as `2|b|/delta` as delta->0: it is dominated by the placement baseline, not
  the shape. (This is the Article-F false positive.)
- Baseline-corrected sorted `(|b+delta s| - |b|)/delta -> s . hat b` (first
  order). It measures the PROJECTION of the continuum shape vector onto the
  digital baseline axis `hat b`. For random `hat b` this averages toward zero and
  has both signs.
- Article-H SIGNED endpoint response: tracks the baseline-lower branch. When the
  branches do not reorder (identity), it is `~ +s . hat b` shifted by the moving
  center; when they reorder (swap), it acquires an extra `-2|b|/delta`-like
  contribution, which is large and negative. The mean over placements is
  therefore `~ (fraction identity)*(+) + (fraction swap)*(-2|b|/delta)`. This is
  the observed identity(+1.7)/swap(-4.25) split and the residual `~ -q0/delta`.
- Identity/swap decomposition: separates the two branches of the sorted/tracked
  map; the swap population carries the branch-order decorrelation.
- Continuum-anchored `p_x/p_y` response (project onto `s`-axis): `~ s . hat s =
  |s|`, the true shape derivative, independent of `b`. This is what the C4v
  symmetry-adapted labeling recovers (there `hat b` is undefined/zero and the
  quadrupole axis is used).
- Basis-invariant split `2|b + delta s|`: for delta small and b != 0 it is
  `~ 2|b| + 2 delta s.hat b`; its delta-DERIVATIVE (the micro-pilot `A`
  eigenvalue split) is `~ 2 s.hat b` plus rotation terms. For b = 0 (C4v) it is
  exactly `2 delta |s|`, giving the clean continuum coefficient.

## When Article-H ~ b.s vs decorrelation statistic

- If `|delta s| << |b|` (generic C1, small delta): the baseline-corrected and
  invariant-derivative observables are `~ s . hat b`, i.e. the continuum shape
  vector PROJECTED on the random digital axis `hat b`. Averaged over placement
  phase, `hat b` decorrelates from `hat s`, so the signed mean is dominated by
  the projection statistics / branch reordering, i.e. a DECORRELATION STATISTIC,
  not `|s|`.
- If `b = 0` (C4v) or one uses the continuum-anchored quadrupole basis: the
  observable is the true `|s|` (the shape derivative), matching `j11^2/j01^2`.

## Check against the data

- C4v (b=0): signed = invariant = +2.8 (n=2), near benchmark 2.54. Consistent
  with the model's `2 delta |s|` branch.
- C1 (b != 0): signed = -0.30 (n=2) while invariant = +2.8. Consistent with the
  model: the invariant split `2|b + delta s|` is positive O(1) (dominated by the
  placement `|b|` rotating), while the SIGNED tracked difference is contaminated
  by branch reordering and `s.hat b` sign flips.
- The audit's identity(+1.7)/swap(-4.25) split and the `~ -q0/delta` residual
  are exactly the model's two-branch structure with a decorrelated `hat b`.

Conclusion: the model reproduces every qualitative feature. It is NOT a proof,
but it pins down that the Article-H signed C1 mean measures a digital
placement-decorrelation statistic (`b`-dominated, `s.hat b` projected), whereas
the physical continuum shape derivative is the invariant split `|s|`
(`= j11^2/j01^2` for the disk), recovered only in the continuum-anchored basis
or for C4v.

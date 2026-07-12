# Protocol addendum 2 (dated 2026-07-12): R5 low-rank Delta-H test, R6 placement-averaged response

Frozen before execution; extends `protocol.md` and `protocol_addendum_1.md`.
Motivated by external review of the R1-R4 results: the R4 weight proxy must be
replaced by an explicit low-rank perturbation matrix, and the single-placement
sawtooth must be compared against the placement-ensemble average.

## R5. Explicit low-rank Delta-H prediction in the doublet subspace

Case: n = 4.0, a = 33.0, xi grid of the base protocol (step 0.25). The domain
shrinks monotonically, so between adjacent xi values sites are only removed.

Embedding (frozen): both geometries act on the old site set; the new
Hamiltonian keeps removed sites as decoupled zero-energy orbitals. Then

  Delta_H = H_new_embedded - H_old = + sum over cut bonds (|s><m| + |m><s|),

a bounded low-rank operator supported on removed sites and their neighbors
(cut-bond hoppings were -1; removing them adds +1 per bond). The decoupled
spurious orbitals sit at E = 0, far from the band bottom, and do not enter the
first-order subspace prediction.

Prediction rule (frozen, no fitted parameters):
- ground state: E0_pred = E0_old + W00, W00 = <psi_0|Delta_H|psi_0>;
- doublet: W_ij = <psi_i|Delta_H|psi_j>, i,j in {1,2} (levels E1, E2 of the
  old geometry); predicted new levels = eigenvalues of
  [[E1_old + W11, W12], [W12, E2_old + W22]].
All psi are eigenvectors of the OLD geometry only (computed before the change,
per the review's anti-hindsight requirement).

Reported metrics (frozen):
- per-step relative errors |pred - actual| / |actual step change| for dE0,
  dE1, dE2 and for the splitting change dSplit;
- Pearson correlation of predicted vs actual dSplit;
- support rule: the low-rank mechanism is called QUANTITATIVE if the median
  relative error of the dSplit prediction is below 25%; otherwise it is
  reported as qualitative agreement only.

## R6. Placement-averaged xi response

Case: n = 4.0, a = 33.0, xi grid of the base protocol; 4x4 translation grid
(offsets {0, 1/4, 1/2, 3/4}^2), theta = 0.

Reported (frozen):
- y(xi; dx, dy) = S/(1-r) per placement; ensemble mean and std per xi;
- total variation TV = sum over adjacent xi of |y(xi_{k+1}) - y(xi_k)| for
  (a) the centered single realization and (b) the ensemble mean;
- the fraction of placements with suppressed response (y < 1) at each xi < 1.
Expectation recorded before running: translations shift the row-crossing
thresholds, so the ensemble mean should be substantially smoother
(TV(mean) < TV(single)) and the mean response at xi < 1 should not be
suppressed to the degree the centered realization is. Whether the mean
approaches the continuum coefficient at small xi is left open.

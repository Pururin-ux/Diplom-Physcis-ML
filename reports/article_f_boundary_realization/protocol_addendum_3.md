# Protocol addendum 3 (dated 2026-07-12): R7 refined ensemble, R8 exact low-rank closure

Frozen before execution; extends the base protocol and addenda 1-2. Motivated
by independent review of the published branch: (i) the xi = 0.25 ensemble bias
in R6 must be tested against quadrature refinement and size; (ii) the R5
qualitative low-rank result must be closed by the exact non-perturbative
(Feshbach / T-matrix) formula.

## R7. Placement ensemble on the 8x8 grid, several sizes

n = 4.0; sizes a in {24, 33, 48}; xi in {0.25, 0.5, 0.75, 1.5, 3.0};
translation grid {0, 1/8, ..., 7/8}^2 (64 points); theta = 0; r = 1 - xi/a.

Reported per (a, xi): ensemble mean and std of y = S/(1-r), fraction of
placements with y < 1, and at a = 33 the direct comparison of the 8x8 mean
with the 4x4 mean from R6 at the shared xi values.

Frozen question: does the upward bias of the mean at xi = 0.25 persist under
grid refinement (4x4 -> 8x8) and under size increase at fixed xi? Persistence
under both would indicate a physical small-deformation bias; shrinking with
grid refinement would indicate a quadrature artifact; shrinking with size
would indicate a finite-size effect. No preferred outcome is declared.

## R8. Exact Feshbach / T-matrix closure of the boundary-event problem

Setup: n = 4.0, a = 33.0. Two steps from the base xi grid: the large
row-crossing event (old domain at xi = 0.75, new at xi = 1.00; 68 removed
sites) and the following small event (old at xi = 1.00, new at xi = 1.25; 10
removed sites).

Exact statement being tested (removal of site set R equals the V -> infinity
limit of an onsite potential on R): the new eigenvalues that carry weight on
R are the zeros of det G_RR(E), where
G_RR(E) = sum_k psi_k(R) psi_k(R)^T / (E - E_k)
is the old-geometry resolvent restricted to the removed sites, built from the
FULL dense eigendecomposition of the old Hamiltonian.

Procedure (frozen):
- full dense symmetric eigendecomposition of the old H;
- new doublet levels located by bisection on sign(det G_RR(E)) inside the
  pole-free intervals (E1_old, E2_old) and (E2_old, E3_old), absolute
  tolerance 1e-12;
- comparison with the directly diagonalized new-geometry levels;
- PASS criterion: |E_pred - E_direct| < 1e-9 for both doublet levels of both
  steps;
- truncation study: repeat with G_RR built from only the lowest
  m in {4, 20, 100, 500} eigenpairs; report the resulting error of the
  predicted levels on the E + 4 scale, to establish how many old modes a
  practical low-rank theory needs.

Interpretation rule (frozen): if PASS, the R5 overestimation is fully
attributed to the neglected multiple-scattering (resolvent) structure, and
the boundary-event mechanism is closed quantitatively by the exact low-rank
formula; the truncation table then quantifies the cost of practical
approximations. If bisection fails or the criterion is not met, the failure
is reported as such.

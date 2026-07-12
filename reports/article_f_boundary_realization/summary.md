# Article-F master summary: fixed-area shape effect vs lattice boundary realization

Protocol: `protocol.md` (frozen before execution, commit `a176396`).
Results: commit `601aa68` (this branch: `article-f-boundary-realization`).
Environment: conda env `diplom-kwant` (Kwant + SciPy); solver startup check
shift-invert vs `which='SA'`: max abs diff 2.8e-14.

## Headline numbers

### 1. Continuum reference (MFS/MPS, unit semi-axis, r_AR = 1)

| n | lambda1 | lambda2 = lambda3 | lam1*A/pi | Q0 | gate |
|---|---|---|---|---|---|
| 1.2 | 8.06697513 | 20.29029896 | 6.040437 | 1.515230 | PASS (drift 2e-8) |
| 2.0 | 5.78318596 | 14.68197053 | 5.783186 | 1.538734 | PASS (Bessel err 8e-10) |
| 3.0 | 5.21631971 | 13.19017870 | 5.866676 | 1.528637 | UNSTABLE at 1e-6 (drift ~2.5e-6) |
| 4.0 | 5.05703172 | 12.73171703 | 5.969020 | 1.517626 | UNSTABLE at 1e-6 (drift ~3e-5) |

Per protocol the 1e-6 stability gate failed for n = 3.0 and 4.0. The R2
parameter-robustness study (addendum 1) sharpened this: n = 3.0 values are
stable to ~4e-6 relative; for n = 4.0, lambda1 is stable to 3.9e-5 while
lambda2 is stable only to 5.4e-4 and must be quoted as 12.731 +/- 0.007
(Q0 = 1.518 +/- 0.001). All of these are still far tighter than the 1-4%
lattice effects compared against them.

Continuum shape effect at fixed area (excess of lam1*A/pi over the disk):
n = 1.2: +4.45%; n = 3.0: +1.44%; n = 4.0: +3.21%. Faber-Krahn ordering holds
(disk minimal). Isotropic Q0 varies by only 1.6% across the family, with the
disk maximal, consistent with the Payne-Polya-Weinberger bound
(Ashbaugh-Benguria): the isotropic optimum of Q is a symmetry/theorem effect,
not a design opportunity.

### 2. Lattice extrapolation agrees with the continuum within its uncertainty
(0.2% for n <= 3, 0.5% for n = 4)

Translation-averaged (4x4 grid) fixed-area lattice series, linear
extrapolation of mean lam1*A_an/pi vs 1/a_circ. The linear variant happens to
land within 0.1% of MFS for all n, but the honest uncertainty of the
extrapolated limit is the full spread over admissible fit schemes (linear,
quadratic, leave-one-scale-out; see R1): about 0.2% for n <= 3 and 0.5% for
n = 4.

| n | TB intercept | MFS continuum | rel. difference |
|---|---|---|---|
| 1.2 | 6.0428 | 6.040437 | +0.04% |
| 2.0 | 5.7796 | 5.783186 | -0.06% |
| 3.0 | 5.8725 | 5.866676 | +0.10% |
| 4.0 | 5.9725 | 5.969020 | +0.06% |

The two-component picture is therefore quantitative: at fixed area,
`lamA(a) = lamA_continuum + c(n)/a_circ + placement scatter`, with fitted
slopes c(n) in [-5.8, -4.0] and translation scatter std decaying roughly as
1/a (exponents -1.08, -1.02, -0.83 for n = 1.2, 2.0, 4.0; the n = 3.0
exponent -0.56 is not reliable, std is non-monotonic over only four scales).

Note: the earlier fixed-a TB-only extrapolation (article-E line) gave
lambda_TB_inf = 8.0300 for n = 1.2 vs the true continuum 8.06698, i.e. a
-0.46% bias — larger than the 0.1% reference-uncertainty gate that blocked
the article-E continuum-residual analysis. With the MFS reference this
shape-sensitive lattice residual is now measurable rather than inconclusive.

### 3. Placement statistics (fixed area, a_circ = 30)

- Translation scatter at fixed angle: std 0.05-0.4% of lamA.
- Orientation effect on the translation-averaged mean: ~0.7-0.8% span for
  both n = 1.2 (monotonic toward 45 deg) and n = 4.0 (non-monotonic, minimum
  at the axis-aligned orientation).
- Translation-grid convergence 4x4 -> 8x8: negligible for n = 1.2 (0.01%),
  0.2% mean shift for n = 4.0 — production runs should use 8x8.
- Placement-induced doublet splitting S_lat at r_AR = 1 is generic:
  mean 0.003-0.013, max 0.033; exact zeros occur only for placements
  preserving C4v (site- and plaquette-centered), consistent with the
  point-group reduction E -> B1 + B2 (C2v) and E -> A' + A'' (Cs).
- Shape contrast n = 1.2 vs 4.0 at theta = 0: 2.0% of lamA; after orientation
  averaging: ~1.2%. The contrast survives placement variation at a_circ = 30
  but is orientation-dependent at the tens-of-percent level of itself.

### 4. xi transition with site-set symmetric differences

For n = 4.0 (and n = 3.0) the response ratio y = S/(1-r) follows a sawtooth
in xi = a(1-r) that collapses across a = 24, 33, 48: y jumps to the continuum
coefficient (~3.0) exactly at the xi values where dN_sym spikes (52-108 sites
— the flat top/bottom boundary rows crossing lattice rows), and decays
between crossings. The previously observed "dip at xi = 1.5" is the middle of
the inter-crossing interval, not an isolated anomaly. Caveat: with integer a,
row crossings coincide with integer xi; the general control variable is the
fractional part of b = a - xi, not xi itself.

For n = 1.2 there is no suppression and no sawtooth (y ~ 1.6-2.1 throughout;
dN_sym spread uniformly): for boundaries inclined to the lattice axes the
site-update thresholds are dense and the response stays quasi-continuous.
n = 2.0 is intermediate. The transition law is therefore boundary-orientation
class dependent, as preregistered in the interpretation rules.

## Interpretation within the frozen rules

1. At fixed area the superellipse exponent changes the ground-state
   functional lam1*A/pi by at most +4.45% (n = 1.2) relative to the disk;
   between non-circular members the spread is 1.2-2.9%. The raw fixed-a
   "shape effect" of tens of percent is area, not shape.
2. The lattice boundary-realization contribution at a_circ ~ 30 is of the
   same order as the shape contrast (translation scatter ~0.1-0.4%,
   orientation ~0.8%, finite-size mean correction ~2-3%), and decays as ~1/a
   with translation averaging.
3. Placement alone lifts the symmetry-protected doublet degeneracy with a
   point-group selection rule; magnitudes reach S_lat ~ 0.03 (equivalent to
   1-2% continuum anisotropy at this size).
4. Small-anisotropy response is governed by lattice commensuration of
   axis-aligned boundary segments (sawtooth in b mod 1), not by a universal
   xi ~ 1 law.

## Deviations from protocol

None in grids or definitions. MFS gate outcomes UNSTABLE for n in {3.0, 4.0}
are reported as required (values quoted with their drift, no silent
fallback). All other analyses ran exactly as preregistered.

## Addendum 1 results (R1-R4, frozen in protocol_addendum_1.md, commit 04e24a1)

R1 — extrapolation-form robustness. The full min-max spread of the continuum
intercept over {linear, quadratic, leave-one-scale-out} variants is 0.18-0.20%
for n in {1.2, 2.0, 3.0} and 0.53% for n = 4.0. The headline "agreement with
MFS to <= 0.1%" above therefore holds for the linear variant but the honest
extrapolation uncertainty is ~0.2% (n <= 3) and ~0.5% (n = 4). This supersedes
the <= 0.1% phrasing; the lattice-continuum decomposition remains valid: the
shape effects being resolved (1.4-4.5%) exceed the extrapolation uncertainty
by a factor of about 22 (n = 1.2), 8 (n = 3.0), and 6 (n = 4.0) — several
times over, not uniformly "an order of magnitude".

R2 — MFS parameter robustness (charge factor x basis, 6 combinations). n = 3.0:
lambda1 and lambda2 stable to ~4e-6 relative (the earlier UNSTABLE flag was
borderline). n = 4.0: lambda1 stable to 3.9e-5 relative; lambda2 only to
5.4e-4 relative — for n = 4.0, lambda2 must be quoted as 12.731 +/- 0.007 and
Q0(n=4) as 1.518 +/- 0.001. An independent non-MFS continuum method remains an
open validation item (recorded in the addendum).

R3 — orientation-effect decay. Delta_theta(a_circ) shrinks with size for both
classes: n = 1.2: 0.047 -> 0.029 over a_circ 24 -> 48 (effective power
p ~ 0.7); n = 4.0: 0.078 -> 0.029 (p ~ 1.3). Three-point estimates only, but
they (i) confirm the orientation correction vanishes toward the continuum and
(ii) suggest different effective decay laws for the diagonal and axis-aligned
boundary classes — a candidate standalone result for the manuscript.

R4 — sawtooth mechanism. Over the 16 xi steps (n = 4.0, a = 33), the level
shifts follow the first-order perturbative weight of the removed sites:
corr(dE1, w1) = +0.97, corr(dE2, w2) = +0.999, corr(dSplit, w2 - w1) = +1.000,
against the raw-count baseline corr = +0.98. Frozen-rule outcome: SUPPORTED.
Final interpretation (superseded by R5, see below and the correction log):
the sawtooth is governed by the low-rank boundary-event operator through the
eigenfunction weight of the removed sites; the bare first order reproduces
the structure of the jumps but not their absolute magnitude.

## Addendum 2 results (R5-R6, frozen in protocol_addendum_2.md, commit f270595)

R5 — explicit low-rank Delta-H test (n = 4.0, a = 33). The bare first-order
prediction from the cut-bond Delta_H in the doublet subspace reproduces the
*structure* of the level shifts essentially exactly — Pearson
corr(dSplit_pred, dSplit_act) = +0.9997 — but systematically overestimates
magnitudes (median relative error ~200%). Frozen-rule outcome: qualitative
agreement only. The overestimation factor is NOT constant: it clusters in two
regimes — about 2.3-3.5 for small boundary events (10-28 removed sites) and
5.37-5.47 for the large lattice-row-crossing events (64-72 removed sites);
see `r5_deltaH_steps.csv`. Site removal is a strong (V -> infinity)
perturbation, so the bare first order in the bounded cut-bond operator
overshoots, and the growth of the factor with event size indicates essential
multiple-scattering processes: a non-perturbative low-rank treatment
(T-matrix / Feshbach elimination of the removed block) is required, not a
single renormalization constant. The earlier R4 phrasing "first-order
perturbation theory" is hereby downgraded accordingly.

R6 — placement-ensemble average of the xi response (n = 4.0, a = 33, 16
translations). The staircase is a fixed-placement property, not an ensemble
property: total variation of y(xi) drops from 7.38 (centered realization) to
0.65 (ensemble mean). The ensemble mean is close to the continuum coefficient
(2.90-3.06) for xi >= 0.5; at the smallest tested deformation xi = 0.25 the
mean is biased upward (3.40) with very large realization scatter (std 2.2,
shrinking to 0.2 by xi = 4), and only 38% of placements are suppressed there.
Nearly all of the residual total variation of the mean comes from the
3.40 -> 2.90 drop between the first two xi points. Conclusion: translation
averaging removes the staircase and restores a near-continuum mean response
already for xi >= 0.5 at this size; at extremely small deformations the
averaging removes stepping but does not yet guarantee quantitative recovery
of the continuum derivative (residual bias + large scatter). Whether the
xi = 0.25 bias is physical or a coarse-quadrature artifact of the 4x4
translation grid is deferred to R7 (8x8 grid, several sizes).

## Provenance

| Item | Path | Commit |
|---|---|---|
| Frozen protocol | `reports/article_f_boundary_realization/protocol.md` | `a176396` |
| Placed geometry + solver + tests | `src/geometry.py`, `src/kwant_solver.py`, `tests/test_placed_superellipse_geometry.py` | `a176396` |
| Run scripts (4) | `scripts/run_article_f_*.py` | `601aa68` |
| Placement stats | `placement_stats_rows.csv`, `placement_stats_aggregates.csv`, `placement_stats_summary.md` | `601aa68` |
| Fixed-area series | `fixed_area_scaling_rows.csv`, `_aggregates.csv`, `_fits.csv`, `_summary.md` | `601aa68` |
| xi transition | `xi_transition_rows.csv`, `xi_transition_summary.md` | `601aa68` |
| Continuum MFS | `continuum_mfs_values.csv`, `continuum_mfs_summary.md` | `601aa68` |
| Execution log | `run_log.txt` | `601aa68` |
| Protocol addendum 1 | `protocol_addendum_1.md` | `04e24a1` |
| Robustness checks R1-R4 | `scripts/run_article_f_robustness_checks.py`, `r1_extrapolation_variants.csv`, `r2_mfs_robustness.csv`, `r3_orientation_decay.csv`, `r4_sawtooth_weights.csv`, `robustness_checks_summary.md` | `324a1a0` |
| Protocol addendum 2 | `protocol_addendum_2.md` | `f270595` |
| R5-R6 checks | `scripts/run_article_f_deltaH_and_ensemble.py`, `r5_deltaH_steps.csv`, `r6_ensemble_rows.csv`, `deltaH_and_ensemble_summary.md` | `b013c84` |

## Correction log

- `<= 0.1%` cross-validation headline replaced by the honest extrapolation
  uncertainty (0.2% for n <= 3, 0.5% for n = 4) after R1.
- MFS "usable at ~1e-5" phrasing replaced by the R2 per-eigenvalue stability
  (n = 3: ~4e-6; n = 4: lambda1 3.9e-5, lambda2 5.4e-4).
- R4 "quantitatively explained as first-order perturbation theory" downgraded
  after R5 to the low-rank boundary-event mechanism with non-perturbative
  magnitudes; the overestimation factor is event-size dependent (2.3-3.5
  small events, ~5.4 row-crossing events), not a single constant.
- R6 "continuum coefficient over the whole grid" narrowed to xi >= 0.5, with
  a biased mean and large scatter at xi = 0.25 (status pending R7).
- "order of magnitude larger" replaced by explicit factors 6-22x.

# Protocol addendum 1 (dated 2026-07-12): robustness checks R1-R4

Frozen before execution; extends `protocol.md` without modifying it. Motivated
by external review of the first article-F results (commits `601aa68`,
`9cfeb26`). No frozen definition from the base protocol is changed.

## R1. Extrapolation-form robustness (post-processing only)

Input: `fixed_area_scaling_rows.csv` (commit `601aa68`).
For each n, fit translation-mean lamA_an vs x = 1/a_circ with:
- (i) linear: L_inf + c1 x (as in the base protocol);
- (ii) quadratic: L_inf + c1 x + c2 x^2;
- (iii) linear leave-one-scale-out (each scale removed once).
Report: all intercepts, fit residuals, the spread of L_inf across variants,
and the comparison of each variant against the MFS reference. No preferred
variant is chosen after seeing results; the reported uncertainty is the full
min-max spread of L_inf over (i)-(iii).

## R2. MFS parameter robustness for n in {3.0, 4.0}

Grid: charge factor in {1.15, 1.2, 1.3} x basis size in {120, 200}
(6 combinations per n), narrow search windows around the known lambda1 and
lambda2 from `continuum_mfs_values.csv`. Reported uncertainty per eigenvalue:
max minus min over the 6 combinations. Printed digits in any later use must
not exceed this uncertainty. The circle is not re-run (already at 1e-9).
An independent non-MFS method remains explicitly out of scope here and is
recorded as an open validation item.

## R3. Orientation-effect decay with size

n in {1.2, 4.0}; a_circ in {24, 48}; theta in {0, 22.5, 45} deg; 4x4
translation grid per cell. Delta_theta(a_circ) = max over theta minus min
over theta of the translation-mean lamA_an, using only the three shared
angles (for a_circ = 30 the stage-1 data are reduced to the same three
angles). Report Delta_theta at the three scales and the effective power p in
Delta_theta ~ a_circ^{-p} from a log-log fit of three points (declared as an
estimate, not a measured law).

## R4. Sawtooth mechanism: perturbative weight of removed sites

Case n = 4.0, a = 33, xi grid of the base protocol. The domain shrinks
monotonically, so site changes between adjacent xi are removals only
(asserted). At each xi step, using normalized eigenvectors of the previous
geometry: w1 = sum over removed sites of |psi_1|^2, w2 = same for psi_2
(levels E1, E2 above the ground state). Report Pearson correlations over the
16 steps:
- dE1_step vs w1; dE2_step vs w2;
- d(E2 - E1) vs (w2 - w1);
- baseline: |d(E2 - E1)| vs removed-site count.
Interpretation rule (frozen): the weighted-site mechanism is called supported
only if the weighted correlations exceed the raw-count baseline correlation.

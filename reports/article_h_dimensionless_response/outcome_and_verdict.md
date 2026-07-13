# Article-H outcome and verdict: dimensionless reanalysis

Reanalysis-only, from Article-G HEAD `2744ef0`. No new eigensolves. All numbers
are recomputed from the frozen Article-G pilot CSVs after restoring the
Article-F normalization by `E0+4`.

## 1. Git commits and remote SHAs

- Protocol (frozen, pushed before results): `29d5da0` on
  `origin/article-h-dimensionless-signed-response`.
- Analysis library, script, tests, results: this commit series (see manifest).
- Parent (Article-G HEAD, unchanged): `2744ef0`.

## 2. Input integrity

Inputs read-only: `pilot_main_rows.csv` (15104 rows), `pilot_conv_rows.csv`
(5120 rows). A regression test asserts the canonical SHA256 of the Article-G
CSV is unchanged after the analysis runs. Derived-row count is exactly 20224.

## 3. Tests

13 Article-H regression tests pass, including: exact recovery of the normalized
sorted metric; exact decomposition `L_old = B_baseline + C_sorted_bc`; the
identity `chih_split = chih_plus - chih_minus`; per-configuration ground-state
normalization; OK/all/ambiguity bounds; forbidden-field guards
(`symmetry_class_delta`, `cut_bonds`); no-iid-p-value output check;
line-ending-invariant hashing; and a **regression against the audit's
representative dimensionless means** (n=4, xi=0.4: -1.056/-1.415/-1.238 at
a0=24.3/33.7/48.2, matched to < 0.03). The previously `if False`-disabled
Article-G test is superseded here by real non-degenerate deformation tests
(Article-G history unchanged).

## 4. Exact observable definitions

Primary: `chih_split = ( q_split(delta) - q_split(0) ) / delta`,
`q_split(cfg) = (Etil_+ - Etil_-)/(E0(cfg)+4)`, each configuration normalized by
its own kinetic scale. Auxiliaries `chih_pm`, `chih_center` analogous. The
raw-energy `chi_split` is retained only for comparison. Identity
`chih_split = chih_plus - chih_minus` holds to < 1e-12 on all rows.

## 5. Article-F normalized decomposition

`L_old = B_baseline + C_sorted_bc` verified to < 1e-9 on all rows. The old
positive Article-F-style metric `L_old` is dominated by the placement baseline
`B_baseline`; subtracting it and tracking signed branches removes the positive
sign.

## 6. Legacy-geometry matched control (n=4, a0=33.7, mode A)

On the SAME `legacy_fixed_major_axis` geometry:

| xi | L_old mean | B_baseline mean | C_sorted_bc mean | signed chih_split mean | median |
|---|---|---|---|---|---|
| 0.05 | +9.011 | +9.425 | -0.414 | -0.901 | -0.180 |
| 0.10 | +4.600 | +4.704 | -0.104 | -0.993 | +0.146 |
| 0.20 | +3.201 | +2.393 | +0.808 | -1.419 | +0.319 |
| 0.40 | +2.896 | +1.233 | +1.663 | -1.288 | -0.708 |
| 0.80 | +2.926 | +0.645 | +2.282 | -0.205 | +2.042 |

The signed means (-0.90, -0.99, -1.42, -1.29, -0.21) match the audit exactly.
Causal conclusion: the disappearance of the old positive sign is due to
baseline subtraction + signed tracking (not the geometry change), and the
signed dimensionless response is O(1) negative, NOT zero, on the same geometry.

## 7. Area-preserving results (primary)

Dimensionless `chih_split` cell means span [-1.438, +0.253]. Sign of the phase
mean: 29/30 fixed-xi cells negative, 20/24 fixed-delta cells negative. For n=4
the means are O(1) negative (~ -0.4 to -1.44); for n=2 smaller (~ -0.01 to
-0.43) and occasionally slightly positive. The dimensionless mean does not
vanish and does not shrink with lattice size.

## 8. OK / all / ambiguity sensitivity

876 AMBIGUOUS rows (margin-driven). Worst-case ambiguity bounds on the mean:
- n=4 cells: the [lo, hi] band stays negative in essentially all cells
  (e.g. n=4, a0=33.7, xi=0.4: [-1.547, -1.071]); sign robust.
- n=2 cells: several bands cross zero (e.g. n=2, a0=48.2, xi=0.4:
  [-0.376, +0.022]); sign NOT robust to ambiguity.
Medians are multimodal and unstable (sign flips across xi and grid). The
SIGN of the mean is ambiguity-robust for n=4 but not for n=2.

## 9. Fixed-xi results

29/30 negative means; magnitude O(1) for n=4. Ambiguous fraction 4-11%.

## 10. Fixed-delta results

20/24 negative means; 4 positive cells (including n=2, a0=33.7, delta=0.001 =
+0.253). Partially overlapping deformation range with fixed-xi
(delta in 0.001-0.008 vs 0.001-0.033). The two paths agree qualitatively (no
restored positive bias) but are not identical; no limit-order claim is made.

## 11. Conditional symmetry-class results (decisive)

At xi=0.4 (counts per class: C1=168, Cs_axis=56, Cs_diag=28, C4v=2, C2v=2):

| class | n=2 mean (24.3/33.7/48.2) | n=4 mean (24.3/33.7/48.2) | note |
|---|---|---|---|
| C1 | -0.41 / -0.30 / -0.26 | -1.28 / -1.31 / -1.25 | dominant, negative, scale-stable |
| Cs_axis | -0.41 / -0.46 / -0.33 | -0.77 / -1.65 / -1.70 | negative, medians near 0 |
| Cs_diag | -0.22 / -1.35 / +0.80 | +2.94 / -2.83 / +1.39 | sign flips; f_amb 0.43-0.86 |
| C4v | +2.09 / +2.81 / +2.83 | +1.69 / +3.54 / +3.52 | only 2 points; positive |

The negative full-phase mean is genuinely present WITHIN the dominant C1
(66% of placements) and Cs_axis (22%) classes, not merely cross-class
cancellation. C1 is O(1) negative and remarkably scale-stable for n=4
(-1.28/-1.31/-1.25). The pooled scalar is contaminated by the small,
heavily-ambiguous Cs_diag class and the 2-point C4v class.

## 12. 16^2 -> 32^2 diagnostics (dimensionless chih_split)

All five anchors: GRID_UNRESOLVED under the frozen Article-H criteria. The
mean criterion is often satisfied (mean_over_sigma <= 0.05 for 4/5 points), but
median/quantile/ECDF criteria fail, driven by multimodality:
- n=4, xi=0.4: mean stable (-1.415 -> -1.327) but median flips (-2.05 -> +0.27);
- n=4, xi=0.1: ECDF D = 0.103, max-quantile/IQR = 0.66.
The distribution is NOT refinement-stable; the mean is more stable than the
median. (The Article-G raw GRID_UNRESOLVED verdict is not rewritten.)

## 13. n=2 vs n=4 distribution comparison

Dimensionless (not a normalization artifact): ECDF D grows 0.15 -> 0.39 with
xi; Wasserstein-1 ~ 0.9-1.7 (large in dimensionless units); n=4 has 2-3x
heavier negative tails (q05_4 ~ -6 to -14 vs q05_2 ~ -3 to -5). No iid
p-values used. Inference levels: finite-grid difference CONFIRMED; refinement
stability NOT established (n=4 tails/medians shift 16->32); scale trend present
but three-point; continuum relevance NOT resolved. Causal link to flat
rational-normal boundary events remains compatible-with, not established (the
`cut_bonds` event diagnostic is invalid and unused).

## 14. Raw vs dimensionless scaling

- Raw std(a): effective exponent ~1.9-2.0 for most fixed-xi cells
  (PRELIMINARY EFFECTIVE a^-2; expected for unnormalized low-energy gaps). This
  is why the Article-G raw response looked like it "vanished".
- Dimensionless std(a): exponent ~ 0 (-0.11 to +0.66, mostly near 0): the
  dimensionless width stays O(1) and does NOT shrink with lattice size.
- Dimensionless mean(a): O(1) across scales, roughly flat for larger xi (n=4,
  xi=0.4: -1.06/-1.42/-1.24; xi=0.2: -0.88/-1.02/-0.87).
No continuum extrapolation from three scales.

## 15. Outcome H1 / H2 / H3

- H3 (dimensionless scalar consistent with zero): **REFUTED.** The
  dimensionless mean and width are O(1); 29/30 and 20/24 cell means negative;
  within-class C1 mean is O(1) negative and scale-stable. Not zero.
- H1 (finite negative dimensionless response supported): **PARTIAL / not
  clean.** Supported for the dominant C1 (and Cs_axis) population: O(1),
  negative, scale-stable, ambiguity-robust for n=4. NOT supported as a clean
  pooled scalar, because for n=2 the sign is not ambiguity-robust, fixed-delta
  has positive cells, and medians are unstable.
- H2 (dimensionless response unresolved): **MET for the pooled scalar.** Sign
  predominantly negative and O(1), but not stable enough across AMBIGUOUS
  treatment (n=2, Cs_diag), medians multimodal, all five grid anchors
  unresolved.

**Verdict: H2 (pooled scalar unresolved), with H3 firmly refuted and a
within-class H1-like negative O(1) signal in the dominant C1/Cs_axis
populations.** The main question is answered: after restoring the dimensionless
normalization the baseline-corrected signed phase response does NOT vanish; it
is finite (O(1)) and predominantly negative, genuinely within the dominant
symmetry classes; but it is not established as a clean, refinement-stable
scalar.

## 16. Distribution status

**FINITE-GRID DIFFERENCE** (confirmed, dimensionless), NOT a
REFINEMENT-STABLE CANDIDATE on current data (n=4 tails/medians shift 16->32).
Scalar outcome and distribution status are kept separate.

## 17. What is established

- The old positive Article-F-style response is an artifact of the unsubtracted
  placement baseline plus gap-sorting (exact decomposition + matched legacy
  control).
- The Article-G "response -> 0 / scalar-null" reading was an artifact of the
  dropped `E0+4` normalization: raw width ~ a^-2, dimensionless width ~ O(1).
- In dimensionless units the corrected response is finite and predominantly
  negative on the studied sizes, with a scale-stable O(1) negative mean in the
  dominant C1 class.
- A finite-grid dimensionless distributional difference between n=2 and n=4.

## 18. What is not established

- A clean pooled scalar (sign not ambiguity-robust for n=2; medians unstable;
  grid unresolved).
- Refinement stability (16->32 unresolved for all anchors) and any continuum
  limit or coefficient.
- Any causal boundary-event mechanism (invalid `cut_bonds`; no event analysis).
- Path-order (fixed-xi vs fixed-delta) or limit non-commutation.

## 19. Decision: is 64x64 needed?

**Conditionally yes, but only as a targeted convergence check on the five
existing nested anchors, and only after a successor protocol conditions the
primary observable on baseline symmetry class and carries ambiguity bounds.**
Rationale against the task's gating: a meaningful hypothesis survives (the
dominant C1 class shows an O(1), scale-stable, ambiguity-robust negative mean,
and the dimensionless width is O(1) rather than vanishing), and the 16->32
mean is not clearly divergent. But the POOLED scalar sign is filtering-
dependent (n=2, Cs_diag) and medians are multimodal, so a naive pooled 64x64
would inherit the same ambiguity. Therefore 64x64 is justified for the
class-conditioned observable on the five anchors (n=2/n=4 at a0=33.7,
xi=0.1/0.4, plus n=4 delta=0.004), area-preserving, theta=0, full 64x64
placement grid, preserving direct 16->32->64 comparison. It is NOT run in this
task.

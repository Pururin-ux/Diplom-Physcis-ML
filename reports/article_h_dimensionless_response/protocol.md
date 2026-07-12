# Article-H frozen protocol: dimensionless reanalysis of the Article-G signed response

Status: publicly timestamped prospective protocol for a COMPREHENSIVE
REANALYSIS and convergence assessment of an ALREADY IDENTIFIED normalization
issue. This is NOT a preregistration of a negative-response discovery: the
independent Article-G audit (`independent_scientific_review_article_g_ru.md`,
SHA256 1E449DD7...3DA7E) already reported several representative dimensionless
values and their sign. What is frozen here is the full set of computed
quantities, criteria, tables, and interpretation rules for the reanalysis.

No new spectral data are produced. No new eigensolves are run (only toy-array
unit tests). This protocol commit is pushed to the remote as a standalone
commit and its SHA recorded before the analysis-result commit.

Branch: `article-h-dimensionless-signed-response`, from the exact Article-G
HEAD `2744ef0cfecff1a7ef9f8b1fbdee80134800ad0b`. Article-G raw CSVs, protocol,
aggregates, `outcome_and_verdict.md`, and history are left unchanged.

## 0. Established starting facts (from the audit, not re-derived here)

- Baseline subtraction, signed branch tracking, and union-space embedding in
  Article-G are mechanically correct.
- The old positive Article-F result is refuted after baseline subtraction and
  signed tracking.
- The Article-G raw CSVs and aggregates are reproducible.
- BUT Article-G removed the Article-F normalization by `E0+4`; the raw-energy
  response therefore shrinks ~a^-2 for trivial low-energy-scale reasons. The
  Article-G "scalar-null / vanishing response" reading is withdrawn.

## 1. Inputs (read-only)

- `reports/article_g_signed_response/pilot_main_rows.csv` (15104 rows)
- `reports/article_g_signed_response/pilot_conv_rows.csv` (5120 rows)
Fields used: `E0_0, Eminus_0, Eplus_0` (baseline ground and TRACKED doublet),
`E0_delta, Eminus_delta, Eplus_delta` (deformed ground and TRACKED branches,
NOT re-sorted), `S0_sorted, Sdelta_sorted`, `delta, xi, dx, dy, theta,
shape_n, scale_a0, deformation_mode, placement_grid, branch_status,
symmetry_class_0`. The fields `symmetry_class_delta` and `cut_bonds` are
INVALID (audit) and are not used for any interpretation.

## 2. Primary dimensionless observable

Per placement p and deformation delta (r = 1 - delta), with tracked branches
Etil_-, Etil_+ (Article-G labels, no re-sorting):

- q_split(p, delta) = (Etil_+(delta) - Etil_-(delta)) / (E0(p, delta) + 4)
- q_split(p, 0)     = (E_+(p, 0) - E_-(p, 0)) / (E0(p, 0) + 4)
- chih_split(p, delta) = ( q_split(p, delta) - q_split(p, 0) ) / delta   [PRIMARY]

Each configuration is normalized by ITS OWN kinetic scale (deformed by
E0_delta+4, baseline by E0_0+4). The raw-energy chi_split is retained only for
comparison, never as the primary physical indicator.

## 3. Auxiliary dimensionless observables

- q_pm(p, delta) = (Etil_pm(delta) - E0(delta)) / (E0(delta) + 4);
  q_pm(p, 0) = (E_pm(0) - E0(0)) / (E0(0) + 4);
  chih_pm = ( q_pm(delta) - q_pm(0) ) / delta.
- q_center(p, delta) = ( (Etil_+ + Etil_-)/2 - E0 ) / (E0 + 4);
  chih_center = ( q_center(delta) - q_center(0) ) / delta.

Frozen algebraic identity to verify on all rows:
  chih_split == chih_plus - chih_minus   (to < 1e-9).
If it fails for the chosen definitions, STOP and explain; do not hide it.

## 4. Exact recovery of the Article-F normalized metric

- q_sorted(p, delta) = Sdelta_sorted / (E0(delta) + 4)
- q_sorted(p, 0)     = S0_sorted / (E0(0) + 4)
- L_old       = q_sorted(delta) / delta
- B_baseline  = q_sorted(0) / delta
- C_sorted_bc = ( q_sorted(delta) - q_sorted(0) ) / delta

Frozen identity: L_old == B_baseline + C_sorted_bc (to < 1e-9). Then compare
C_sorted_bc against the signed chih_split to separate: (1) placement baseline,
(2) positive gap-sorting, (3) real signed normalized response.

## 5. Geometry separation (never mixed)

`area_preserving` and `legacy_fixed_major_axis` are tabulated separately. The
existing legacy-control slice (n=4, a0=33.7, mode A only) is analyzed as the
causal control: it shows the old normalized sorted metric, its baseline term,
the sorted-baseline-corrected metric, and the signed normalized metric on the
SAME geometry, so that the disappearance of the old positive sign is
attributed to baseline subtraction + signed tracking, not to the geometry
change. The column `legacy_raw_ratio` is explicitly described as an
UNNORMALIZED legacy-form observable on the given geometry, not the full
Article-F metric.

## 6. Derived table (new file; originals untouched)

`article_h_dimensionless_rows.csv`, one row per input row (exactly 20224),
fields: shape_n, scale_a0, deformation_mode, delta, xi, dx, dy, theta, grid,
branch_status, symmetry_class_0, E0_0, Eminus_0, Eplus_0, E0_delta,
Eminus_delta, Eplus_delta, raw_chi_minus, raw_chi_plus, raw_chi_center,
raw_chi_split, q_minus_0, q_plus_0, q_center_0, q_split_0, q_minus_delta,
q_plus_delta, q_center_delta, q_split_delta, dimless_chi_minus,
dimless_chi_plus, dimless_chi_center, dimless_chi_split, normalized_sorted_raw
(= L_old), normalized_baseline_term (= B_baseline), normalized_sorted_bc
(= C_sorted_bc). No `symmetry_class_delta`, no `cut_bonds`.

## 7. AMBIGUOUS handling (three versions)

For every aggregate produce:
- A. OK-only: branch_status == OK.
- B. All-row endpoint: all rows with the published assignment.
- C. Ambiguity sensitivity bounds: for AMBIGUOUS rows compute BOTH endpoint
  permutations (identity = as-stored; swap = flip Etil_-, Etil_+). For the
  MEAN, report the min and max over worst-case assignment of the ambiguous
  subset. For MEDIAN and quantiles, report all-identity-ambiguous and
  all-swap-ambiguous values and their range, and flag any sign change. No
  incorrect analytic bound is invented for order statistics.
AMBIGUOUS rows are never silently dropped. Central question: is the SIGN of
the phase mean of chih_split stable to AMBIGUOUS treatment?

## 8. Full statistics (frozen)

For each (n, a0, deformation_mode, path [fixed-xi | fixed-delta], parameter
value, grid) report for chih_split: count total, count OK, ambiguous fraction,
mean, std, median, min, max, q05, q25, q75, q95, negative fraction, positive
fraction, zero fraction, IQR, and the ECDF (sorted values). The same, more
compactly, for chih_minus, chih_plus, chih_center. No standard error or
p-value without a stochastic sampling model.

## 9. Conditional statistics by baseline symmetry class (frozen)

Conditional aggregates over `symmetry_class_0` in {C1, Cs_axis, and centered
classes if enough points}. For each class: count, mean, median, std, negative
fraction, ambiguous fraction. Central question: does a zero/negative full
phase mean arise WITHIN each class or by cancellation BETWEEN classes? A class
effect is not declared established if the class has too few points (< 16).

## 10. Fixed-xi vs fixed-delta (frozen)

Analyzed separately. Report for each path: dimensionless means and medians,
scales, sign, ambiguity sensitivity, distribution width, negative fraction.
Allowed statement only: "finite sequences show specified trends over partially
overlapping deformation ranges." No claim of path equality, limit
non-commutation, or continuum limit.

## 11. Convergence 16x16 -> 32x32 (frozen diagnostic criteria)

Only the five existing anchors: (2,33.7,xi=0.1), (2,33.7,xi=0.4),
(4,33.7,xi=0.1), (4,33.7,xi=0.4), (4,33.7,delta=0.004). The Article-G
GRID_UNRESOLVED verdict is NOT rewritten. For Article-H, apply to the
dimensionless chih_split the frozen criteria (report each separately; do not
collapse to one relative-mean error):
- |Delta mean| / sigma_pooled <= 0.05
- |Delta median| / IQR_pooled <= 0.05
- max_q |Delta q| / IQR_pooled <= 0.10
- ECDF D <= 0.05
- W1 / IQR_pooled <= 0.05
- |Delta f_neg| <= 0.03, |Delta f_amb| <= 0.03
This is diagnostic reanalysis, not a change of the Article-G frozen verdict.

## 12. n=2 vs n=4 distribution comparison (frozen)

Use ECDF distance and Wasserstein-1 distance, and differences of mean, median,
IQR, and tails, plus conditional symmetry-class distributions. NO iid KS
p-values. Separate four inference levels: (1) finite-grid difference; (2)
stability under 16->32; (3) scale trend; (4) continuum relevance. Do not
causally attribute any difference to flat rational-normal segments (the event
diagnostic `cut_bonds` is invalid). Allowed: "the observed distributional
difference is compatible with, but does not establish, a coherent
digital-boundary-event mechanism."

## 13. Scaling analysis (frozen)

For raw AND dimensionless observables, fit mean(a), std(a), IQR(a) over the
three scales. Report fitted exponent, residuals, pairwise exponents,
leave-one-point sensitivity, and the explicit impossibility of a reliable
asymptotic from three points. For raw-energy widths, the allowed status is at
most `PRELIMINARY EFFECTIVE a^-2 SCALING`. For the dimensionless observable,
check whether mean, width, and sign remain O(1) and stable. No continuum
extrapolation.

## 14. Frozen outcome set

- H1 (finite negative dimensionless response supported): on the available
  sizes, the dimensionless full-phase mean has a stable negative sign, stable
  to AMBIGUOUS sensitivity; fixed-xi and fixed-delta do not restore a positive
  bias; magnitude stays O(1). A FINITE-SIZE result, not a continuum claim.
- H2 (dimensionless response unresolved): sign or magnitude unstable;
  AMBIGUOUS treatment changes the conclusion; paths disagree; conditional
  populations preclude a single scalar interpretation.
- H3 (dimensionless scalar consistent with zero): means and medians small in
  the dimensionless scale, sign unstable, ambiguity bounds include symmetric
  zero, no stable conditional means. NOT declared merely because raw energy
  shrinks.

Distribution status (separate, never merged with the scalar outcome):
FINITE-GRID DIFFERENCE | REFINEMENT-STABLE CANDIDATE | NOT RESOLVED.

## 15. Tests (frozen list, section 17 of the task)

1. exact recovery of the Article-F normalized sorted metric;
2. exact decomposition L_old = B_baseline + C_sorted_bc;
3. correct signed normalized response;
4. identity chih_split = chih_plus - chih_minus;
5. same-placement baseline;
6. correct endpoint ground-state normalization;
7. OK-only, all-row, and ambiguity bounds;
8. no iid p-values in outputs;
9. no use of symmetry_class_delta;
10. no use of cut_bonds as evidence;
11. derived-row count exactly 20224;
12. no modification of the original raw CSVs;
13. regression against the audit's representative normalized means;
14. fresh-clone portable manifest hashes using a documented hashing
    convention (canonical LF bytes).
Also fix the future regression test disabled via `if False` (in Article-H
tests only; Article-G history is not rewritten).

## 16. Provenance and reporting

`run_manifest.md`: source branch and exact parent SHA, protocol commit,
analysis-code commit, exact commands, Python/package versions, input CSV
SHA256, output SHA256, input/output row counts, an explicit statement that NO
new eigensolves were run, and the line-ending/hashing convention. Do not claim
all analysis scripts were prospective if any is added with results.
`outcome_and_verdict.md`: the 19-section structure of task section 19, ending
with a 64x64 recommendation (which is NOT run here) governed by task section
20.

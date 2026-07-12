# Article-G pilot outcome (frozen criteria, protocol sections 10-11)

Decision made strictly against the frozen §11 criteria. No claim is declared a
success automatically.

## Evidence (corrected observable: signed, baseline-subtracted, branch-tracked)

Primary observable `chi_split` (area_preserving, mode A), across all
n in {2,4} x a0 in {24.3,33.7,48.2} x xi cells:

- cell means span [-0.0118, +0.0001]; median |cell mean| = 0.0019, i.e. the
  central tendency is at the 1e-3 level while the per-cell std is
  6e-3 .. 4e-2 — the mean is not distinguishable from zero.
- median frac_neg = 0.49 (range 0.36-0.54): the signed response is symmetric
  about zero, not a positive bias.
- branch-crossing fraction (tracked upper branch falls below tracked lower)
  reaches ~0.49-0.51 at xi = 0.4, 0.8 for both shapes: about half the
  placements have the two branches cross, which the old sorted metric
  (>= 0 by construction) could not represent.
- std(`chi_split`) shrinks by ~3.8x from a0 = 24.3 to 48.2 (a-ratio 1.98),
  i.e. std ~ a^-1.95: the whole signed-response distribution narrows toward a
  delta at zero as the lattice refines. There is no finite nonzero continuum
  coefficient.

Decisive legacy-vs-signed comparison (n=4, a0=33.7, mode A):
| xi | legacy_raw mean | sorted_bc mean | signed chi_split mean | chi_split median |
|---|---|---|---|---|
| 0.05 | +0.0408 | +0.0000 | -0.0018 | 0.0000 |
| 0.40 | +0.0131 | +0.0076 | -0.0062 | -0.0089 |
| 0.80 | +0.0127 | +0.0099 | -0.0041 | +0.0034 |

The legacy metric's apparent positive response (~0.01-0.04, the old "plateau"/
"positive bias") is entirely the placement baseline S(0)/delta plus the
sorted-order-statistic. After subtracting S(0,p) AND tracking signed branches,
the mean response collapses to ~0 (slightly negative, ~half of placements
negative).

Residual distributional signal (candidate object, NOT established here):
- n=2 vs n=4 `chi_split` distributions differ significantly at every matched
  (a0, xi): KS distance grows from ~0.18 (xi=0.05) to ~0.35 (xi=0.8), all
  p < 1e-3.
- n=4 (flat axis-aligned segments) has heavier negative tails: q5 ~2x more
  negative than n=2 (e.g. a0=33.7, xi=0.05: -0.054 vs -0.028) and larger std
  at small xi. This is the coherent-boundary-event signature (flat rational-
  normal segments -> larger, more coherent site-removal jumps).

## Convergence (16x16 -> 32x32, five pre-registered points)

All five points return GRID_UNRESOLVED under the frozen thresholds. The cause
is diagnostic, not a hidden finite signal: the primary mean is ~0, so its
relative change (criterion <= 2%) explodes (e.g. -0.0002 -> -0.0008 gives 336%)
even though the absolute change is ~5e-4. Quantile relative changes are
moderate (0.09-0.76) and negative-fraction changes small (0.003-0.040). The
distribution is roughly grid-stable; the mean-based criterion is simply
inapplicable to a near-zero quantity. Recorded honestly as GRID_UNRESOLVED per
the frozen rule; no silent grid expansion.

## Outcome determination (frozen §11)

- Outcome A (continuum response recovered): NOT MET. There is no finite
  nonzero coefficient; the signed response narrows toward zero as a0 grows.
- Outcome B (distributional effect): PARTIALLY MET. n=2 vs n=4 distributions
  differ significantly (KS, tails, event coherence on flat segments), which is
  a real, physically interpretable difference. But the frozen "stable under
  refinement" clause is not cleanly demonstrated (mean-based convergence is
  unresolved; only one nested refinement level at the anchor points), so this
  is a CANDIDATE object, not an established result.
- Outcome C (corrected effect vanishes): MET for the central tendency. Mean
  and median are near zero, ~half of placements give a negative signed
  response, and the distribution converges toward zero under lattice
  refinement.

**Verdict: primarily Outcome C, with a genuine but unestablished Outcome-B
residual.** The corrected observable refutes the old R6/R7 positive
shape-response; the surviving candidate is the shape-dependent DISTRIBUTION /
boundary-event statistics, not any mean response. Per Outcome C's frozen
instruction, the shape-response-as-a-scalar line is stopped; only the
placement-induced splitting fact at delta = 0 (S(0,p) with its point-group
selection rule) is retained as established, and the distributional difference
is flagged for a separate, properly powered study.

## Deviations from protocol

None in observables, grids, or fields. The frozen definitions were executed as
written. The convergence criterion returned GRID_UNRESOLVED at all anchor
points; this is reported, not worked around. Legacy control was run only for
the labelled slice (n=4, a0=33.7, mode A) as specified.

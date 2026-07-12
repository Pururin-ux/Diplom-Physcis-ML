# STATUS: partial retraction of the Article-F small-deformation interpretation

Date: 2026-07-12. Added on branch `article-g-signed-shape-response`
(base `article-f-clean`). This file is additive: the Article-F `summary.md`,
protocols, scripts and CSVs are left unchanged as a record of what was done.
It is NOT re-edited to read as if Article-F had been correct from the start.

## What is retracted

The R6/R7 interpretation of `S(delta, p) / delta` as a small-deformation
"shape response" is withdrawn. Reasons:

1. **No baseline subtraction.** R6/R7 used the ratio `S(delta,p)/delta` with
   `S = E2 - E1`, without subtracting the placement-induced baseline
   `S(0, p)`. For a generic (non-C4v) placement the baseline splitting
   `S(0,p)` is already nonzero, so `S(delta,p)/delta` mixes the pre-existing
   placement splitting with any true deformation response. The reported
   "plateau" and the "xi = 0.25 upward bias" are therefore not established as
   properties of the deformation response.

2. **Sorted magnitude, not a signed branch response.** `S = E2 - E1 >= 0` is
   the sorted absolute gap between two energy-ordered levels, not the signed
   response of two physically tracked branches. Under deformation the two
   doublet branches can move in opposite directions and can cross; a sorted
   gap cannot represent that and folds sign information into a non-negative
   magnitude. The correct observable requires tracking the two physical
   branches through the deformation (see the Article-G protocol).

## What remains valid (unchanged, still usable as input data)

- The direct Kwant spectra and the geometric/site-set data of Article-F
  (fixed-area series, placement rows, xi rows, MFS reference) remain valid raw
  data and are reused as inputs where relevant.
- The fixed-area continuum-vs-lattice decomposition of E0 (sections 1-3 of the
  Article-F summary) does not depend on the doublet-response error and is not
  retracted here.
- The placement-induced degeneracy lifting *as a static fact at delta = 0*
  (S_lat at r = 1, with the point-group selection rule) is a statement about
  `S(0,p)` itself and stands; only its use inside a `/delta` response ratio is
  affected.

## Clarifications on R8

- The R8 "exact closure" (new levels as zeros of `det G_RR(E)`) is the standard
  Schur-complement / Feshbach identity for the principal submatrix obtained by
  removing a set of sites. It is an algebraic integrity check, **not** a
  novelty claim.
- The R8 truncations `G_RR^{(m)}` with `m < |R|` are mathematically
  inadmissible (the removed-site block requires the full resolvent to be
  represented exactly); the truncation table in the Article-F summary must be
  read only as a demonstration that naive truncation fails, not as an
  approximation scheme.

## Continuation

The corrected observable and a minimal decisive pilot are defined in
`reports/article_g_signed_response/protocol.md` (frozen before computation).

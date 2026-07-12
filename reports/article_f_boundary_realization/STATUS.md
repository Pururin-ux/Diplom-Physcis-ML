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

## Additional interpretation defects identified by the independent review

The independent review (`independent_scientific_review_article_f_ru.md`,
2026-07-12, verdict class E) documented further Article-F interpretation
errors beyond the R6/R7 defect. They are recorded here for honesty; the raw
spectra and geometry remain valid, but the following headline phrasings in
`summary.md` are not supported and should not be carried forward:

- **R4 "SUPPORTED" is literally false.** The frozen addendum-1 rule requires
  every weighted correlation to exceed the raw-count baseline. Independently,
  corr(dE1, w1) = 0.9731 < raw-count baseline 0.9831; the code only tested the
  split correlation. The correct frozen outcome is NOT SUPPORTED (or, if only
  the splitting was intended, the criterion was changed post hoc). Individual
  w1, w2 are also basis-dependent inside the degenerate subspace.
- **"Exact zeros only for C4v" is too narrow.** In the present real,
  time-reversal-symmetric Hamiltonian the first-excited doublet is protected by
  C4v OR by C4 + time reversal (the m = +-1 complex-conjugate irreps form a
  real 2D representation). At a generic rotation the mirrors can be lost while
  C4 remains and the splitting is still numerically zero.
- **MFS model spread is a sensitivity envelope, not an uncertainty**, and the
  n = 3, 4 continuum values were used for comparison despite failing the
  protocol's own stability gate; lambda2(n=4) should be quoted as ~12.73, not
  to eight decimals.
- **"No deviations from protocol" is incorrect** (R4 rule failed; MFS
  comparison used after a failed gate).
- **R8 "exact closure" is the standard Jacobi/Schur principal-minor identity**
  (det G_RR(E) = det M_CC(E)/det M(E)); it is an algebraic integrity check,
  not a new mechanism, and "R5 overestimation fully attributed to multiple
  scattering" overstates it. The R8 truncations with m < |R| are not merely
  inadmissible but identically singular (rank(G_RR^(m)) <= m < |R| forces
  det = 0), so their reported sign changes are floating-point artifacts.
- **"Universal plateau" and "predominantly physical bias"** are not
  established (three sizes; uncorrected sorted order statistic).
- **"Preregistered"** describes a prospective LOCAL ordering only; the remote
  reflog shows each protocol/addendum was first pushed together with its
  results, so this is not an independent public preregistration. (Article-G
  corrects this: its protocol commit `0fa6cbe` was pushed to the remote and
  its SHA confirmed BEFORE any result commit.)

## Continuation

The corrected observable and a minimal decisive pilot are defined in
`reports/article_g_signed_response/protocol.md` (frozen before computation).
The independent review's recommended research direction (phase-averaged signed
digital shape derivative and boundary-event statistics) coincides with the
Article-G observable.

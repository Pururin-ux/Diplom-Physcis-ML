# Discrepancy prediction (attempt) and status

Goal (protocol section 11): before any large distribution pilot, derive at least
one pre-checkable quantitative prediction from lattice-point discrepancy theory,
or declare the comparison not yet defined.

## Weighted-event model

At an event, one lattice site `r` (with its <=4 incident bonds) is added or
removed. To first order in the projected doublet basis, the jump of the
compressed operator is

  Delta B^(2) ~ sum over changed bonds/site of W_r,
  W_r ~ (boundary amplitude of doublet modes at r) x (changed hopping/onsite),

i.e. a sum over boundary sites weighted by the doublet eigenfunction boundary
amplitudes. The response is `A = (1/delta) sum_{events in [0,delta]} W_event`.

## Scaling skeleton (checkable, but constant not derived)

- Number of events over `[0,delta]`: perimeter x normal displacement / spacing
  `~ (2 pi a0) x (a0 delta / 2) ~ a0^2 delta = a0 xi`. At fixed `xi` this GROWS
  linearly in `a0` (many events), so the fixed-xi response is an average over
  `O(a0 xi)` events, not a few.
- Doublet boundary amplitude on the disk scales as `~ 1/a0` (normalized p-mode
  normal derivative amplitude squared integrates to O(1) over the perimeter),
  and each event carries kinetic weight `~ 1/a0^2`.
- The lattice-point discrepancy of a smooth strictly convex body (circle, n=2)
  has variance over translations scaling as `~ a0^{1/2}` (circle problem,
  Kendall/Hardy), whereas convex bodies with FLAT points in RATIONAL-normal
  directions (n=4 axis-aligned segments) have anomalously larger, direction-
  sensitive discrepancy (Brandolini-Colzani-Gariboldi-Gigante-Travaglini 2020).

Predicted (qualitative, direction of the effect only): the placement-to-placement
VARIANCE of the invariant response should scale differently for n=2 (curved,
generic-normal) vs n=4 (flat, rational-normal), with n=4 heavier and more
translation-sensitive. This is consistent with the observed heavier n=4 tails,
but is exactly what discrepancy theory already predicts.

## Prediction table

| Prediction | Observable | Expected scaling | Literature source | What would falsify it |
|---|---|---|---|---|
| Event count grows with size | # events over [0,delta] | ~ a0 * xi | perimeter x displacement (elementary) | sublinear/superlinear count |
| Variance of response, curved n=2 | Var over placements of invariant split | tied to circle discrepancy variance ~ a0^{1/2}-type | Kendall; Iosevich-Sawyer-Seeger (2007) | different exponent for n=2 |
| Variance of response, flat rational n=4 | same, n=4 | anomalously larger, direction-sensitive | Brandolini et al., Rev. Mat. Iberoam. 36 (2020) | n=4 not heavier than n=2 |
| Constant / exact tail law | tail quantiles of the response | NOT DERIVED | (would need the weighted-event law explicitly) | - |

## Status

`DIRECT DISCREPANCY COMPARISON NOT YET FULLY DEFINED`.

A qualitative, direction-of-effect prediction exists and is ALREADY what
discrepancy theory predicts (so a match would be a KNOWN result, outcome V4). No
exact quantitative tail law has been derived that would distinguish our
eigenfunction-marked spectral response from the bare lattice-point discrepancy.
Per the protocol, the next large distribution pilot is therefore FORBIDDEN until
such a quantitative, discriminating prediction is derived.

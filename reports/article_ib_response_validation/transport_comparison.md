# Transport comparison

## Raw overlap vs polar transport

The 2x2 overlap `M2 = U Sigma W^T` is nearly orthogonal (`sv_min ~ 0.999`), so
the polar factor `Q = U W^T` is close to `M2` and the two constructions
`A_M = (M2 D2 M2^T - B0)/delta` and `A_Q = (Q D2 Q^T - B0)/delta` agree to about
1 percent in the split. Transport (raw vs polar / Kato) is therefore NOT the
source of instability.

## Where the instability actually lives

The instability is between two INEQUIVALENT construction families, not between
transport variants:
- deformed-eigenbasis projection (two-state, multi-state, polar) — mutually
  consistent;
- fixed-baseline-mode compression (exact Rayleigh-Ritz) — the correct
  first-order object;
these disagree by ~2x (up to 5x), far beyond any transport-level difference.

Because the failure is already decisive at the construction level and the
transport variants agree with each other, a dense sequential Kato-polar
transport along `0=delta_0<...<delta_N=delta` would not rescue the object: it
would still be built on the deformed-eigenbasis projection and would inherit the
event-driven jump structure documented in `event_scan_analysis.md`. The
sequential transport is therefore not pursued as a fix; it cannot convert a
piecewise-constant, event-driven jump process into a transport-stable
derivative.

## Answer to the main transport question

The eigenvalue pair and invariant split are STABLE under transport choice (raw
M vs polar Q: ~1%), but they are NOT stable under the construction/embedding
choice (deformed projection vs fixed-mode compression: ~50-460%). Since
different admissible constructions change the result by an amount far larger
than the claimed effect, the Article-I invariant micro-pilot is NOT validated
as a construction-independent observable.

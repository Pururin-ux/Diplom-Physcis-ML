# The canonical event-resolved spectral process

## Definition

At fixed shape `n`, size `a0`, placement `p=(x0,y0)`, orientation `theta`, the
digital domain `S(delta)` is piecewise constant in `delta` (proved in
Article-Ib: `piecewise_constant_operator.md`). Let `0 < delta_1 < delta_2 < ...`
be the thresholds where `S` changes; between them `S` is constant. At event `e`:

  S_e^- = S just below delta_e,  S_e^+ = S just above,
  A_e = S_e^+ \ S_e^-  (added sites),  R_e = S_e^- \ S_e^+  (removed sites).

An event may add AND remove sites simultaneously (a SWAP, invisible to a site
count), and may bundle several symmetry-related sites.

The marked spectral event is
`E_e = (delta_e, A_e, R_e, dE_{0,e}, dE_{1,e}, dE_{2,e}, dg_e, dc_e, marks)`
with `dE_{j,e} = E_j(S_e^+) - E_j(S_e^-)`, `g=E_2-E_1`, `c=(E_1+E_2)/2`.

## Why this is canonical (and the Article-Ib object was not)

Each `E_j(S)` is the physical eigenvalue of an actual finite digital domain.
The shift `E_j(S_e^+)-E_j(S_e^-)` is a difference of two well-defined numbers and
requires:
- NO branch labels (each E_j is an ordered eigenvalue of a real symmetric matrix);
- NO transport (no identification of two Hilbert spaces is needed to subtract two
  scalars);
- NO common Hilbert space or embedding;
- NO eigenvector gauge (only eigenVALUES enter).

This is exactly what the Article-Ib response matrix lacked: that object required
choosing a compression, a transport, and a truncation, and was unstable to those
choices. The event shift removes all of them.

It is NOT a derivative and is never called one. Admissible names: spectral event
shift, digital boundary-event mark, event-resolved spectral jump, marked spectral
jump process.

## Additive dimensionless normalization

One fixed scale per placement, `K_ref = E_0(S(0)) + 4`. Marks
`eta_{j,e} = dE_{j,e}/K_ref`, etc. Because the denominator is fixed, marks are
exactly ADDITIVE (telescoping):

  sum_{delta_e <= delta} eta_{g,e} = (g(S(delta)) - g(S(0))) / K_ref.

Hence the cumulative process `J_g(delta) = sum_{delta_e<=delta} eta_{g,e}` is the
true normalized change of the gap, and its formal event measure
`dJ_g = sum_e eta_{g,e} delta(delta - delta_e)` is a marked point process, not a
derivative. Dividing a single event by an inter-event spacing (as Article-H
implicitly did via `/delta`) is what manufactured a spurious "response"; the
fixed-reference additive marks avoid it.

## Relation to Article-H

The Article-H fixed-denominator endpoint response `J_g(delta)/delta` is a
coarse-grained AVERAGE EVENT RATE (total normalized gap change divided by delta),
NOT a derivative. Interpreting it as a per-placement shape derivative was the
original error; as an event-rate it is meaningful but is a statistic of the
discrete event process.

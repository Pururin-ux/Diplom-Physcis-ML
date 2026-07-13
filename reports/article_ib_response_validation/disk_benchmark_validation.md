# Disk benchmark validation (careful)

The analytic coefficient `j11^2/j01^2 = 2.538734` is a FROZEN continuum
benchmark (derived + MFS-verified in Article-I; the derivation stands). Here we
ask, cautiously, whether the LATTICE exact-compression response for symmetric
n=2 C4v placements approaches it.

## Data (exact large-barrier compression, n=2, C4v, dimensionless split)

| placement | a0=24.3 | a0=33.7 | a0=48.2 |
|---|---|---|---|
| (0,0) | 1.464 | 0.547 | (see CSV) |
| (0.5,0.5) | 0.000 | 3.304 | (see CSV) |

The two C4v placements at a single size differ by the full range [0, 3.3], and
neither placement's value is monotone in a0. This is the event-driven scatter of
`event_scan_analysis.md`: at a single small delta and fixed a, the exact
compression is dominated by whether a boundary event has occurred, not by the
continuum slope.

## Status

`NOT CONVERGED`. Individual symmetric-placement lattice responses at these sizes
and this single delta are event-dominated and do NOT show a controlled approach
to `2.5387`. The benchmark is reproduced only in the continuum sense (the MFS
ellipse computation in Article-I), not by a fixed-a fixed-delta lattice
response. Permitted statements: the continuum benchmark is exact and
independently verified; the lattice fixed-a response is event-dominated and not
converged; a controlled approach would require an event-average over delta
and/or placements in the large-a (regime-3) limit, which is out of scope here.

We explicitly do NOT claim "same order", "trending toward benchmark", or
"consistent within discretization error" for the single-placement single-delta
lattice numbers: the placement-to-placement scatter (0 to 3.3) is larger than
the benchmark itself.

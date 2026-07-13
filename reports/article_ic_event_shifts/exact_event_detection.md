# Exact event detection

## Analytic thresholds

For the area-preserving deformation `a_x = a0/sqrt(1-delta)`,
`a_y = a0*sqrt(1-delta)`, a lattice site `(x,y)` (relative to the placement
center) lies on the boundary when
`|x/a_x|^n + |y/a_y|^n = 1`. With `t = (1-delta)^{n/2}`,

  |x|^n t + |y|^n / t = a0^n   =>   |x|^n t^2 - a0^n t + |y|^n = 0.

This is a QUADRATIC in `t`, solved in closed form; each real root `t>0` gives an
exact threshold `delta = 1 - t^{2/n}`. For `x=0` the linear branch gives
`t = |y|^n/a0^n`. All thresholds in the frozen range `(0, dmax]` are collected
per site (`src/article_ic_events.py::site_thresholds`). No uniform scan is used
to FIND events; the scan is used only as an independent completeness check.

## Bundling and event construction

Thresholds within `1e-7` are bundled into one event (simultaneous / symmetry-
related crossings). Between consecutive thresholds `S(delta)` is constant. The
distinct-domain sequence `S_0, S_1, ...` is built by evaluating `S` at midpoints
and de-duplicating consecutive equal sets. Each transition `S_{i-1} -> S_i` with
`S_{i-1} != S_i` is an event; `added = S_i \ S_{i-1}`, `removed = S_{i-1} \ S_i`.

## Event defined by set inequality, not site count

An event is `S_{i-1} != S_i` (frozenset inequality), which correctly captures
SWAP events (one site added and one removed at the same threshold, leaving
`len(S)` unchanged). The Article-Ib detector, which used `len(S)` changes, would
miss swaps; this is fixed here and covered by a dedicated test.

## Completeness check

The analytic threshold list is validated against a very dense uniform delta scan
(the Article-Ib `validation_event_scan.csv` and the `event_process_summary.csv`
telescoping identity): the sum of per-event spectral shifts over a placement must
equal the endpoint spectral change (telescoping), which fails if any event is
missed. The telescoping residual is reported and tested to be ~0.

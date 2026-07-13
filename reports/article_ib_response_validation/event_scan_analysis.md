# Event-resolved delta scans

Dense delta scans (exact large-barrier compression, Bexact) for four
representative placements at a0=33.7, delta in (0, 0.03].

## Findings

- The response changes ONLY at boundary events (site enters/leaves). Between
  events the split is a smooth `(accumulated jump)/delta` curve; at each event
  it jumps. Examples:
  - n=2, (0,0), C4v: split stays EXACTLY 0.000 through several early events,
    then jumps 0.000 -> 0.740 at the event near delta=0.0074. 15 events in
    (0,0.03].
  - n=2, (0.31,0.17), C1: split 0.000 until delta~0.0030, then jumps to 0.652,
    then 1.260, ... 29 events.
  - n=4, (0.6875,0.75): split jumps at essentially every event, non-monotonic:
    2.45 -> 1.24 -> 0.45 -> 0.34 -> 0.27 -> 0.62 -> 0.42 ... 38 events.

- The value at any fixed delta depends on WHICH events have occurred by that
  delta. Two placements of the SAME symmetry class and size give entirely
  different responses (e.g. the two C4v placements gave exact splits 1.464 vs
  0.000 at a0=24.3, and 0.547 vs 3.304 at a0=33.7): the difference is the event
  pattern, not a shape derivative.

## Answers to the scan questions

1. Does the response arise continuously or only in jumps? Only in jumps: it is
   an event-driven step/finite-difference quantity, consistent with the proven
   piecewise-constant operator.
2. Is it set by one big event or many? Both occur: some placements are dominated
   by a single early event (n=2 (0,0)), others by a sequence (n=4 (0.6875,0.75)).
   No single universal structure.
3. Is there a meaningful coarse-grained slope after event-averaging? Possibly, in
   the fixed-delta large-a limit (regime 3), but NOT at fixed a for a single
   placement. Any such slope is an event-density average, not a derivative.
4. Is the fixed-xi observable a statistic of event number/weight? Yes. The
   number of events over [0,delta] scales roughly as perimeter x normal
   displacement ~ a0 x (a0 delta) = a0 xi, and the response is the
   eigenfunction-weighted sum of these events divided by delta. It is a digital
   boundary-event statistic, not a shape derivative.

## Consequence

The response is intrinsically event-driven. This is fully consistent with the
piecewise-constant-operator proof and inconsistent with calling the 2x2 object a
"shape-derivative matrix" at fixed lattice size. A well-defined DIGITAL observable
would have to be an explicit event-averaged statistic (fixed construction, fixed
transport), not a per-placement "derivative".

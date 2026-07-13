# Event-mechanism analysis

Data: `event_rows.csv` (1262 events across 32 placements),
`event_process_summary.csv` (per-placement process).

## Canonical process is well-defined (E1 evidence)

- Exact event enumeration is COMPLETE: per placement, the telescoping identity
  `sum_e Delta g_e = g(S_final) - g(S_initial)` holds with maximum residual
  0.0e+00 over all 32 placements. The analytic thresholds miss no events.
- Marks use eigenvalues only: basis-, transport-, and gauge-independent.
- Mean events per placement ~ 39 over `xi in [0,0.8]` (grows with size as
  expected, ~a0*xi).

## Endpoint response is built from MANY WEAK events, not a few big ones

Largest single-event fraction of the total absolute gap variation: median 0.05,
range [0.02, 0.14]. So the endpoint gap change is an accumulation of many small
events, each a finite-rank site/bond change. This directly answers the main
process question (protocol section 13): the Article-H-style endpoint response
`J_g(delta)/delta` is a coarse-grained AVERAGE over many weak boundary events,
NOT a single coherent jump and NOT a derivative.

## What predicts a single event's spectral mark

From the discrepancy gate (`discrepancy_model_comparison.md`):
- The doublet GAP mark `eta_g` is poorly predicted by bare geometry
  (Model 0 R^2 = 0.41) but well predicted once eigenfunction-weighted finite-rank
  marks are added (Model 1 R^2 = 0.91). This is the known statement that the
  gap shift is the differential boundary MATRIX ELEMENT (Schur self-energy
  w2 - w1), not the site count.
- The doublet CENTER mark `eta_c` is already well predicted by geometry
  (R^2 = 0.86): it tracks the mean level, closer to an area/Weyl response.

## Mechanism is textbook finite-rank

Each event is an add/remove of sites and bonds: a finite-rank perturbation whose
eigenvalue shifts obey the Schur secular equation and Cauchy interlacing
(`finite_rank_event_theory.md`, toy-verified in tests). The eigenfunction
weighting that "wins" the gate is precisely the finite-rank matrix element /
Krein-Schur self-energy. There is no residual structure in the marks beyond this
known theory in the present micro-pilot.

## Reading

The event object is canonical and validated (E1), but its physics is known
finite-rank perturbation + lattice-point discrepancy (E2). The eigenfunction
weighting is the known matrix element, with a direct literature analog. No
structure beyond known theory is demonstrated.

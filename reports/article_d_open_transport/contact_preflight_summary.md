# Open Transport Contact Preflight Summary

## Scope

This is a contact-coupling preflight for a new open-transport direction.
Closed-spectrum Path B is not continued. No FD continuum references,
TB-vs-FD residuals, closed-spectrum shape contrast, ML, inverse design,
Q/S objectives, magnetic ranking crossover, or thesis/diploma edits are
used.

## System Definition

- square-lattice tight-binding model
- onsite `0`, nearest-neighbor hopping `-1`
- spinless two-terminal conductance convention: `G=T`
- superellipse dot: `a=30.0`, `rAR=1.0`
- flat one-lattice-column contact slices at `x=+-a` define the strip-lead interface

## Lead And Energy Definition

- two symmetric square-lattice strip leads
- lead widths tested: `W=4` and `W=10`
- energy window: `[-3.8, -3.0]`
- energy points: `241`

## Phase 0A: Contact-Width Result

- contact_effect_size, n=2.0 W4 vs W10: `0.6589809313045025`
- shift/rescale contact distance: `0.24323761388169962`
- smatrix failure count: `0`

## Phase 0B: Shape-Vs-Contact Comparison

- shape_effect_size_W4: `0.5810925658201803`
- shape_effect_size_W10: `0.5122909816541278`
- lead width dominates: `True`

## Kill Tests

- mode thresholds explain features: `False`
- straight-channel baseline computed: `True`
- straight-channel mean distance: `0.5282601064806791`
- straight-channel baseline killed: `False`
- energy-shift/rescale collapse killed: `False`

## Strongest Observed Feature

- `n4.0_W10 total_variation=80.37942281570045, maxima=-3.7833333;-3.7766667;-3.7633333;-3.71;-3.7033333;-3.6766667;-3.67;-3.65;-3.6366667;-3.62;-3.61;-3.59, minima=-3.79;-3.78;-3.7666667;-3.7066667;-3.6733333;-3.6633333;-3.6433333;-3.6166667;-3.6033333;-3.5733333;-3.5633333;-3.5233333`

## Final Verdict

`OPEN_TRANSPORT_PREFLIGHT_KILLED_CONTACT_DOMINANCE`

A larger open-transport shape scout is recommended only for
`OPEN_TRANSPORT_PREFLIGHT_CONTACT_STABLE_PROMISING`.

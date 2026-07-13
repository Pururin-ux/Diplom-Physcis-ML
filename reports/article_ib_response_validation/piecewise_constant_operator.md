# The digital Hamiltonian is piecewise constant in delta

## Claim and proof

Claim: at fixed lattice size `a`, the tight-binding Hamiltonian `H(delta)` is a
piecewise-constant (step) function of `delta`, changing only at isolated
"boundary events" where a lattice site enters or leaves the domain.

Proof. The domain is the binary set
`S(delta) = { r in Z^2 : g_r(delta) := |r_x/a_x(delta)|^n + |r_y/a_y(delta)|^n <= 1 }`
with `a_x = a0/sqrt(1-delta)`, `a_y = a0*sqrt(1-delta)`. For each fixed lattice
point `r`, `g_r(delta)` is continuous (indeed smooth) in `delta`. Membership of
`r` flips exactly at the isolated zeros of `g_r(delta) - 1`. Only finitely many
lattice points lie near the boundary, so the set of flip thresholds
`{delta_1 < delta_2 < ...}` is finite and discrete on any bounded delta-interval.
Between two consecutive thresholds the set `S(delta)` is constant, hence the
sparse Hamiltonian (onsite 0, hopping -1 on nearest-neighbor pairs within
`S(delta)`) is constant. At a threshold, one site (and its <=4 incident bonds)
is added or removed: a finite-rank jump. QED.

Consequences:
- `dH/ddelta = 0` for all `delta` outside the finite event set, and is
  UNDEFINED (a finite jump) at each event. There is no ordinary derivative of
  `H` with respect to `delta` at fixed `a`.
- Any `A = (B(delta) - B(0))/delta` is a FINITE DIFFERENCE across the events in
  `[0,delta]`, i.e. `A = (1/delta) * sum over events of the projected jump`. It
  is an endpoint/event statistic, not a derivative.

Therefore the Article-I quantities must NOT be called a "Hadamard derivative",
a "shape-derivative matrix", or a "first-order lattice derivative". Admissible
terms: finite-difference endpoint response matrix; event-averaged response;
digital boundary-event statistic.

## Four distinct regimes

1. Continuum derivative. The smooth domain `Omega(delta)` has a genuine
   Hadamard shape derivative of the doublet (the disk value `j11^2/j01^2`).
   This is a property of the CONTINUUM family, not of any fixed lattice.
2. Finite-`a` digital jump process. At fixed `a`, `B(delta)` is a step function;
   `A` is a finite difference over `O(number of events in [0,delta])` jumps.
   Not a derivative.
3. Fixed-`delta` continuum limit (`a -> infinity`, `delta` fixed). The boundary
   sweeps `~ a*delta` lattice spacings, the event density grows, and the
   event-averaged `A` is expected to converge (by Mosco / norm-resolvent
   convergence of pixelated domains) to the continuum Hadamard response. This is
   the regime in which "derivative" language is legitimate, in the limit only.
4. Fixed-`xi = a*delta` double scaling (`a -> infinity`, `delta -> 0`). The
   boundary sweeps a FIXED `O(xi)` lattice spacings, so only `O(xi)` events
   occur. `A` is then a statistic of a finite number of discrete boundary
   events and their eigenfunction weights: a genuine digital object, NOT a
   continuum derivative. This is the only regime with any novelty potential and
   is exactly where lattice-point discrepancy theory applies.

The Article-I micro-pilot used small fixed `delta` at fixed `a`, i.e. regime 2,
and reported eigenvalues of the finite-difference `A`. Its interpretation as a
"shape-derivative matrix" is only valid in the regime-3 limit, not at fixed `a`.

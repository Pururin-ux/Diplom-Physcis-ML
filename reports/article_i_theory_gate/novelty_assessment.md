# Novelty assessment and the two scaling programs

## Two distinct programs (protocol section 8) — never merged into one continuum claim

### Continuum shape-response program
Limit: `a -> infinity`, `delta` fixed (or `delta -> 0` after `a -> infinity`),
so the boundary displacement `delta * a` is large in lattice units and the
discretization error is controlled.
- Physical question: what is the shape derivative of the first-excited doublet
  of the smooth domain?
- Primary observable: basis-invariant eigenvalue pair / split of the 2x2
  Hadamard matrix (dimensionless).
- Known literature: Hadamard shape derivatives (degenerate case), ellipse
  membrane splitting, discrete-to-continuum spectral convergence. FULLY KNOWN.
- Expected novelty: none — the disk value `j11^2/j01^2 = 2.5387` is textbook;
  the lattice reproduces it.
- Numerical limit needed: large-`a` series and/or FEM/BEM continuum reference.
- Stop criterion: once the invariant lattice split extrapolates to the
  Hadamard/FEM value, the program is closed (confirmatory, not novel).

### Digital double-scaling program
Limit: `a -> infinity`, `delta -> 0`, `xi = a*delta = const`, so the boundary
moves by O(1) lattice spacings and digital boundary events do not disappear.
- Physical question: what is the distribution of the class-conditioned digital
  doublet response as a marked function of lattice phase, orientation, and
  boundary-event structure?
- Primary observable: the full (non-Gaussian) distribution of the INVARIANT
  split and of the signed decorrelation statistic, conditioned on baseline
  symmetry class; its tails for flat/rational-normal (n=4) vs curved (n=2)
  boundaries.
- Known literature: lattice-point discrepancy for convex bodies with flat
  points and rational normals (Brandolini et al.; Gariboldi), which controls
  translation-variable counting anomalies; pixelation spectral convergence.
- Expected novelty: the eigenfunction-MARKED (spectral) version of these
  counting anomalies, in the double-scaling regime, was not found in the
  searched literature. Candidate, not established.
- Numerical limit needed: nested `16->32->64` phase grids at fixed `xi` (the
  audit's targeted run) PLUS a boundary-event mechanism analysis (saved
  add/remove site sets, run lengths, local normals, mode boundary weights).
- Stop criterion: if the invariant-split distribution collapses onto the
  discrepancy-theory prediction (known), or if the class-conditioned statistics
  fail to stabilize, the program yields no new result.

## Three theses

### Thesis A — sorted-gap + unsubtracted placement baseline can fake a positive shape response
- Known: order-statistic / absolute-value folding and baseline subtraction are
  elementary; analogous "baseline" critiques are standard in ML-for-science.
- Our data show: the exact decomposition `L_old = B_baseline + C_sorted_bc` and
  the matched legacy control quantitatively demonstrate the artifact in this
  concrete spectral setting.
- Missing: nothing for the claim itself; it is fully supported.
- Journal novelty: 2/10 (methodological, not physical; a cautionary note).
- Minimal new result for publication: generalize to >1 discretization/tracker
  to make it a broadly useful methodological lesson.

### Thesis B — in the double-scaling regime there is a nontrivial distribution of the effective doublet response
- Known: the placement-averaged response and lattice-point discrepancy
  framework; the response is O(1) in dimensionless units (not vanishing).
- Our data show: a reproducible, class-conditioned, non-Gaussian distribution;
  the INVARIANT split is positive O(1); the signed statistic is a decorrelation
  measure; `C1` (full-measure) dominates. Finite-grid difference n=2 vs n=4 is
  real.
- Missing: refinement stability (16->32 unresolved for the full distribution),
  a mechanism tying tails to boundary events, and a direct comparison to
  discrepancy theory.
- Journal novelty: 4-5/10 (a mesoscopic digital-boundary spectral-statistics
  object; conditional on establishing refinement stability and novelty vs
  discrepancy theory).
- Minimal new result: a refinement-stable, mechanism-backed class-conditioned
  distribution shown to differ from the bare discrepancy prediction.

### Thesis C — flat, rationally oriented boundary segments produce shape-dependent heavy tails
- Known: exactly the regime of lattice-point discrepancy with isolated flat
  points and rational normals (Brandolini et al.; Gariboldi) — heavy/anomalous
  behavior for rational-normal flat segments is expected.
- Our data show: n=4 (flat segments) has 2-3x heavier negative tails than n=2;
  compatible with, but not proof of, coherent boundary events (the `cut_bonds`
  diagnostic is invalid and unused).
- Missing: a correct boundary-event diagnostic and a direct match/mismatch to
  the discrepancy asymptotics; without it, the effect may BE the known
  discrepancy phenomenon.
- Journal novelty: 3-5/10, but at high risk of being a known discrepancy result
  re-expressed spectrally.
- Minimal new result: show the spectral (eigenfunction-marked) tails deviate
  quantitatively from the bare lattice-point discrepancy prediction.

## Bottom line on novelty

The continuum shape-response line is KNOWN TEXTBOOK physics and must not be
presented as a new effect. The only line with any novelty potential is the
digital double-scaling spectral statistics (Thesis B/C), and even there the
natural theory (lattice-point discrepancy with flat points/rational normals) is
developed, so novelty is NOVELTY NOT ESTABLISHED until a direct comparison and a
mechanism are provided.

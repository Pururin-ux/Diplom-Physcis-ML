# Preregistered protocol: fixed-area shape effect and lattice boundary realization (article F line)

Status: frozen before execution. Any amendment requires a new dated commit and
cannot apply retroactively (same rule as the S-objective preregistration).

Scope approval: this analysis line was explicitly requested by the project
owner (July 2026) after the limitations-audit review. It supersedes neither
the thesis nor the article-E audit; it is a new physics line about separating
the continuum shape effect from the lattice boundary-realization effect.

## Model

Square-lattice nearest-neighbor tight-binding dot, onsite 0, hopping -1,
hard-wall open boundary (thesis convention). Kinetic scale `E_kin = E + 4`.
Direct Kwant calculation is the source of truth. Solver: sparse eigsh with
shift-invert around `-4.2` (strictly below the band bottom, so ordering is
safe); consistency with `which='SA'` is enforced by an automated test and a
startup check recorded in each report.

## Placed geometry

Discrete domain: integer lattice points `(x, y)` such that the point
translated by `-(x0, y0)` and rotated by `-theta` satisfies
`|u/a|^n + |v/b|^n <= 1`. Single shared predicate
`src/geometry.py::in_placed_superellipse` is used by the Kwant builder and by
all site-set diagnostics.

## Definitions (fixed before running)

- `A_an(n, a, b) = 4 a b Γ(1+1/n)^2 / Γ(1+2/n)` — analytic area.
- Fixed-area sizing: for circle-equivalent scale `a_circ`, the semi-axis is
  `a(n) = sqrt(pi * a_circ^2 / f(n))`, `f(n) = A_an / (a b)`, with `b = a`.
- `lamA_sites = (E0 + 4) * N_sites / pi` — site-normalized shape functional.
- `lamA_an = (E0 + 4) * A_an / pi` — analytic-area-normalized functional.
  Both are reported everywhere; continuum disk reference `j01^2 = 5.78319`.
- `S = (E2 - E1) / (E0 + 4)` — doublet splitting measure.
- `S_lat` — the same quantity evaluated at `r_AR = 1` (isotropic continuum
  shape), so any nonzero value is placement-induced.
- `xi = a * (1 - r_AR)` — boundary displacement in lattice units along the
  compressed axis.
- Symmetric difference between consecutive xi points:
  `dN_sym = |added| + |removed|` where added/removed are sites entering or
  leaving the discrete domain between adjacent xi grid values.

## Parameter grids (frozen)

1. Placement statistics (`run_article_f_placement_stats.py`)
   - Shapes: n in {1.2, 4.0}; r_AR = 1; fixed-area scale a_circ = 30.
   - Translation grid convergence at theta = 0: offsets {0, 1/4, 1/2, 3/4}^2
     (16 points) and {0, 1/8, ..., 7/8}^2 (64 points).
   - Angle scan: theta in {0, 11.25, 22.5, 33.75, 45} degrees, each with the
     16-point translation grid.
   - Reported: per-cell E0..E3, N_sites, lamA (both norms), S_lat; per-angle
     mean and std over translations.

2. Fixed-area scaling (`run_article_f_fixed_area_scaling.py`)
   - n in {1.2, 2.0, 3.0, 4.0}; scales a_circ in {24, 30, 36, 48}; plus
     a_circ = 72 for the contrast pair n in {1.2, 4.0}. theta = 0.
   - 16-point translation grid per (n, a_circ).
   - Reported: mean/std of lamA (both norms) per (n, a_circ); linear fit of
     mean lamA_an vs 1/a_circ (intercept = continuum estimate, declared as an
     extrapolation estimate, not a proof); power-law fit of std vs a_circ.

3. xi transition (`run_article_f_xi_transition.py`)
   - n = 4.0 at a in {24, 33, 48}; n in {1.2, 2.0, 3.0} at a = 33.
   - xi in {0.25, 0.5, ..., 4.0} (step 0.25), r = 1 - xi/a, centered
     placement (x0 = y0 = 0, theta = 0).
   - Reported: N_sites, added/removed/dN_sym vs previous xi point, S,
     y = S/(1-r), doublet mean shift from xi = 0.
   - Placement dependence of the transition is explicitly out of scope here.

4. Continuum reference (`run_article_f_continuum_mfs.py`)
   - Method of particular solutions with fundamental-solution basis and
     Betcke-Trefethen interior-point QR regularization; domain r = 1,
     n in {1.2, 2.0, 3.0, 4.0}, semi-axis 1.
   - Acceptance gate: circle validation must reproduce j01^2 and j11^2 with
     relative error < 1e-6, and values must be stable at the reported digit
     under basis-size increase; otherwise the method is reported as failed
     (no silent fallback).
   - Reported: lambda1, lambda2 (=lambda3 by symmetry), lamA_an/pi, continuum
     Q(0) = lambda2/lambda1 - 1.

## Success/interpretation rules (frozen)

- No claim of a universal xi ~ 1 law; the tested hypothesis is that the
  suppression threshold for the axis-aligned boundary class (n = 4) collapses
  in xi across sizes, and that the n = 1.2 (diagonal boundary) class shows no
  such suppression in the tested xi range.
- Placement-induced splitting is interpreted via point-group reduction
  (site/plaquette centers preserve C4v; bond centers reduce to C2v; generic
  diagonal offsets to Cs). Exact zeros are expected only for C4v placements.
- The lattice-vs-continuum comparison is made against the MFS values only if
  the MFS acceptance gate passes.
- Translation statistics are quadrature summaries over the placement cell,
  not random-sample statistics; no sigma-based significance language.

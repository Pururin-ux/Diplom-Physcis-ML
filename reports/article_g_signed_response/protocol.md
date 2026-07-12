# Article-G frozen protocol: signed, baseline-subtracted, branch-tracked shape response

Status: FROZEN before any computation. This document is committed and pushed
to the remote as a standalone commit; the remote SHA is recorded, and no
result commit is produced until this protocol commit is confirmed on the
remote. This is a publicly timestamped prospective protocol only if the
protocol commit demonstrably precedes the result commits on the remote.

Amendments after seeing results are forbidden. Any change is a new dated
`addendum_k.md`, committed and pushed BEFORE the computation it governs.

Branch: `article-g-signed-shape-response` (base `article-f-clean`).
Model, lattice, solver conventions: unchanged from Article-F (spinless
nearest-neighbour tight binding, onsite 0, hopping -1, hard wall; kinetic
scale E + 4; shift-invert eigensolver cross-checked vs which='SA').

## 0. Motivation (accepted as the starting problem, not defended)

The Article-F R6/R7 "small-deformation response" is withdrawn (see
`reports/article_f_boundary_realization/STATUS.md`). Two defects are accepted
as given: (i) `S(delta,p)/delta` was not baseline-subtracted by `S(0,p)`;
(ii) `S = E2 - E1 >= 0` is a sorted magnitude, not a signed two-branch
response. Article-G defines the corrected observable and runs a minimal
decisive pilot whose only question is:

> After baseline subtraction and signed branch tracking, does a meaningful
> placement-averaged shape response survive at all?

No attempt is made to reconfirm the old positive result.

## 1. Geometry and deformation (frozen)

Placed superellipse (single shared predicate, extends Article-F placement
code): continuum shape `|u/a_x|^n + |v/a_y|^n <= 1`, center `(x0, y0)`,
in-plane rotation `theta` (pilot: theta = 0). r = 1 - delta.

Two deformation modes, never silently mixed; both recorded per row in
`deformation_mode`:

- `area_preserving` (PRIMARY):
  `a_x = a0 / sqrt(r)`, `a_y = a0 * sqrt(r)`  ->  `a_x * a_y = a0^2`,
  so the analytic area `f(n) a_x a_y = f(n) a0^2` is constant in delta.
  This isolates pure shape change from area change.
- `legacy_fixed_major_axis` (CONTROL ONLY):
  `a_x = a0`, `a_y = a0 r` (area changes as a0^2 r). Computed only as a
  labelled control column; never the primary observable.

## 2. Branches and observables (frozen)

For each placement `p = (x0, y0, theta)` and deformation `delta`, solve the
baseline `H0(p) = H(delta=0, p)` and the deformed `H_delta(p)`. Let the ground
state have index 0; the "doublet" is the next pair, baseline levels
`E1(0) <= E2(0)` with vectors `psi1(0), psi2(0)`, and deformed levels
`E1(d) <= E2(d)` with vectors `phi1(d), phi2(d)`.

Branch tracking is done in the UNION site space of the baseline and deformed
domains: each eigenvector is embedded by zero-padding on sites absent from its
own domain, then renormalized. Overlaps use the embedded vectors.

Overlap matrix (2x2 complex): `M_ij = <psi_i(0) | phi_j(d)>`,
`O_ij = |M_ij|^2`. Assignment permutation `pi` (identity or swap) maximizes
`O_{1,pi(1)} + O_{2,pi(2)}` (full two-state enumeration; equivalent to
Hungarian for 2x2). Tracked deformed energy of baseline branch i:
`Etil_i(d) = E_{pi(i)}(d)`.

Branch labels (frozen): `-` := baseline-lower branch (i = 1),
`+` := baseline-higher branch (i = 2). Thus `E_-(0) = E1(0)`,
`E_+(0) = E2(0)`, and `Etil_-(d), Etil_+(d)` are their tracked deformed
energies. `+` and `-` are physically tracked branches, NOT re-sorted levels.

Signed, baseline-subtracted observables (per delta; PRIMARY):

- `chi_minus  = (Etil_-(d) - E_-(0)) / delta`
- `chi_plus   = (Etil_+(d) - E_+(0)) / delta`
- `chi_center = ( 0.5*(Etil_+ + Etil_-)(d) - 0.5*(E_+ + E_-)(0) ) / delta`
- `chi_split  = ( (Etil_+ - Etil_-)(d) - (E_+ - E_-)(0) ) / delta`

`chi_center` and `chi_split` are invariant under any orthogonal rotation
within an exactly degenerate baseline subspace and are the PRIMARY signed
observables. `chi_split` is signed: it goes negative when the tracked branches
approach or cross, which the sorted metric cannot represent.

Legacy / comparison metrics (recorded, NOT the physical response):

- `legacy_raw_ratio = (E2(d) - E1(d)) / delta`  (the withdrawn R6/R7 metric)
- `sorted_baseline_corrected_ratio = ((E2(d)-E1(d)) - (E2(0)-E1(0))) / delta`
  (sorted-gap baseline correction; equals `chi_split` only when the tracked
  assignment is the identity, i.e. no crossing — the difference between the
  two exposes crossings).

## 3. Symmetry classes and degenerate-baseline handling (frozen)

Placement point group (theta = 0), from the center offset modulo 1:

- `cx, cy in {0, 0.5}` with both -> lattice C4 center -> `C4v`
  (centers (0,0) and (0.5,0.5)): baseline doublet exactly degenerate.
- exactly one of cx, cy in {0, 0.5} (e.g. (0.5,0), (0,0.5)) -> `C2v`:
  baseline generically split (p_x, p_y in distinct 1D irreps).
- cx = cy (diagonal, e.g. (0.25,0.25)) -> `Cs` (sigma_d): baseline generically
  split; no M_x/M_y.
- otherwise -> `C1`.

Note: on the theta = 0 square lattice every C4 center ((0,0),(0.5,0.5)) is
also mirror-symmetric (site group C4v); no pure-C4-without-mirror placement
occurs, so the C4+T-protected case does NOT arise in this pilot and is out of
scope. Smoke test 4 asserts that no pilot placement is classified pure C4.

Handling by class:

- `C1`, `Cs`, `C2v` (baseline non-degenerate): overlap-based tracking above.
  `chi_minus`, `chi_plus` are individually well defined.
- `C4v` (baseline exactly degenerate): individual `psi1(0), psi2(0)` are
  basis-arbitrary. Use the full 2D subspace. `chi_center` and `chi_split`
  remain well defined and basis-invariant (there `chi_split` reduces to
  `(E2(d)-E1(d))/delta` with a correctly ZERO baseline, i.e. the
  baseline-subtraction defect is absent by construction). For the individual
  `chi_minus/chi_plus`, build the symmetry-adapted basis inside the degenerate
  subspace by diagonalizing the reflection `M_x` (x -> 2*x0 - x); assign
  `-` := the `M_x`-odd (p_x-like) member and `+` := the `M_y`-odd (p_y-like)
  member. Record `symmetry_class_0 = C4v_symmetry_adapted`.

## 4. Reliability and ambiguity (frozen)

Per placement/delta compute:

- `subspace_sv_min` = smallest singular value of the 2x2 `M`
  (= cos of the largest principal angle between the two 2D subspaces);
- `subspace_sv_max` = largest singular value of `M`;
- `assignment_score_best`, `assignment_score_second` over the two permutations,
  `assignment_margin = best - second`.

`branch_status = OK` iff `subspace_sv_min >= 0.90` AND
`assignment_margin >= 0.10`; otherwise `branch_status = AMBIGUOUS`.
AMBIGUOUS rows are NOT dropped: they are written to CSV and counted; they are
excluded from headline means of `chi_minus/chi_plus` and reported as a
separate fraction. `chi_center` and `chi_split` (basis-invariant) are still
reported for AMBIGUOUS rows but flagged.

## 5. Parameter grids (frozen)

Shapes: `n in {2, 4}` (smooth circle; near-flat axis-aligned segments).
Scales (non-integer, to avoid synchronizing row crossings across scales):
`a0 in {24.3, 33.7, 48.2}`. Orientation: `theta = 0`.

Mode A (fixed xi = a0 * delta): `xi in {0.05, 0.10, 0.20, 0.40, 0.80}`,
`delta = xi / a0`.
Mode B (fixed delta): `delta in {0.001, 0.002, 0.004, 0.008}` (mandatory; the
old work only probed the diagonal delta ~ 1/a path).

Placement grid (main): `16 x 16`, `dx, dy in {0, 1/16, ..., 15/16}`.

Convergence grid `32 x 32` computed ONLY at these pre-registered points
(no post-hoc additions):
- `n=2, a0=33.7, area_preserving, xi=0.10` and `xi=0.40` (Mode A);
- `n=4, a0=33.7, area_preserving, xi=0.10` and `xi=0.40` (Mode A);
- `n=4, a0=33.7, area_preserving, delta=0.004` (Mode B).

## 6. Smoke tests before the pilot (frozen; all must PASS)

Written to `reports/article_g_signed_response/smoke_report.md`:
1. generic placement with nonzero `S(0,p)` (baseline already split);
2. site-centered `C4v` placement (exact baseline degeneracy);
3. plaquette-centered `C4v` placement (exact baseline degeneracy);
4. assert NO pilot placement is classified pure-C4-without-mirror;
5. artificial two-level order-swap: branch tracking must follow identity, not
   sorted order;
6. union-space embedding: overlaps of a state with itself across differing
   site sets are consistent and normalization holds;
7. basis invariance: random orthogonal rotation inside an exactly degenerate
   baseline subspace leaves `chi_center`, `chi_split` unchanged (< 1e-10);
8. legacy confound decomposition identity:
   `legacy_raw_ratio = S(0)/delta + sorted_baseline_corrected_ratio` holds to
   < 1e-9.
The production run starts only after all smoke tests PASS.

## 7. Raw CSV fields (frozen; every individual placement saved)

`shape_n, scale_a0, deformation_mode, delta, xi, dx, dy, theta,
n_sites_0, n_sites_delta, added_sites, removed_sites, symmetric_difference,
cut_bonds, E0_0, Eminus_0, Eplus_0, E0_delta, Eminus_delta, Eplus_delta,
S0_sorted, Sdelta_sorted, legacy_raw_ratio, sorted_baseline_corrected_ratio,
chi_minus, chi_plus, chi_center, chi_split, overlap_11, overlap_12,
overlap_21, overlap_22, assignment_score_best, assignment_score_second,
assignment_margin, subspace_sv_min, subspace_sv_max, branch_status,
symmetry_class_0, symmetry_class_delta`

Here `Eminus_0 = E1(0)`, `Eplus_0 = E2(0)`, `Eminus_delta = Etil_-(d)`,
`Eplus_delta = Etil_+(d)` (tracked, not sorted). Aggregates alone are not
sufficient; all individual placement rows are stored.

## 8. Statistics (frozen)

For each `(n, a0, deformation_mode, mode/parameter)` and for each of
`chi_minus, chi_plus, chi_center, chi_split, legacy_raw_ratio,
sorted_baseline_corrected_ratio`, report over the OK placement ensemble:
mean, std, median, min, max, quantiles {5,25,75,95}%, fraction negative,
fraction AMBIGUOUS (of all placements), plus ECDF and histogram arrays and a
(dx,dy) heatmap of the primary `chi_split`. Check and report multimodality,
heavy tails, skew, mean-vs-median divergence, and dependence on positive
sorting. The phrases "universal plateau" and "physical positive bias" are
forbidden until after the corrected analysis.

## 9. Convergence criteria (frozen)

At the pre-registered points, going 16x16 -> 32x32, for the primary
`chi_split` (and secondarily `chi_center`):
- |mean change| <= 2%; |median change| <= 2%;
- |{5,25,75,95}% quantile change| <= 5% each;
- |negative-fraction change| <= 0.03 absolute.
If any fails: mark that point `GRID_UNRESOLVED`. The grid is NOT expanded
silently; expansion requires a dated addendum first.

## 10. Success / failure criteria (frozen)

The pilot is meaningful iff, after baseline subtraction and branch tracking,
at least one holds:

- Outcome A (continuum response recovered): ensemble mean/median of the
  corrected response are grid-stable, scale-consistent, and approach a finite
  coefficient.
- Outcome B (distributional effect): mean may be small/zero but the n=2 vs
  n=4 distributions differ physically and statistically (tails,
  multimodality, negative fraction, event-size dependence), stable under
  refinement.
- Outcome C (corrected effect vanishes): mean/median near zero, shape
  differences unstable, distributions converge. Then the shape-response line
  is honestly stopped and only the narrower placement-induced symmetry-
  splitting statement (a delta=0 fact) is retained.

No outcome is declared a success automatically; the criteria are applied as
written.

## 11. Explicit exclusions for this task (frozen)

Out of scope here: independent FEM/BEM continuum solver; full orientation
scan; other lattices; manuscript; target-journal analysis; magnetic field;
transport; ML; approximate T-matrix theory; new interpretations of R8. The
exact R8 identity may be used only as an algebraic integrity check; no
`G_RR^(m)` truncation with `m < |R|`. No claim of limit non-commutation; the
pilot only compares fixed-xi and fixed-delta paths.

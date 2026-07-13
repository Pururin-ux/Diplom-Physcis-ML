# Physical invariance of the Article-H observable

Central question (protocol section 5): can the negative C1 signed mean be
published as a self-standing physical quantity, or is it admissible only as an
explicitly label-dependent digital statistic?

## Label-dependent vs basis-invariant quantities

The first-excited response lives in a 2D (nearly) degenerate subspace. Its
first-order response is the 2x2 symmetric matrix `A = dH^(2)/ddelta` in that
subspace. Quantities split into two groups.

Label-dependent (change under a global relabeling / choice of axes in the
degenerate subspace):
- the SIGNED branch difference `E_+ - E_-` and hence Article-H `chih_split`
  (flips sign under `+ <-> -`);
- the identity/swap-population means separately;
- lower/upper baseline-energy tracking.

Basis-invariant (independent of the arbitrary basis in the degenerate subspace):
- `tr A` (doublet-center response);
- the unordered PAIR of eigenvalues of `A` (the two level slopes);
- `|lambda_+(A) - lambda_-(A)|` (invariant split magnitude);
- the traceless Frobenius norm `||A - (1/2)tr A * I||`;
- the principal-axis rotation of `A` (defined mod 90 deg);
- the subspace leakage (weight of the deformed doublet outside the baseline
  doublet).

The continuum Hadamard matrix for the disk is `diag(-1,+1) * j11^2 delta/(2a0^2)`;
its invariants are: eigenvalue pair `{-1.269, +1.269}` (dimensionless), split
magnitude `2.5387`, `tr = 0`, traceless norm `= 2.5387` (dimensionless), all
independent of any labeling.

## Micro-pilot evidence (n=2, near-disk; leakage <= 2.4e-3, reconstruction valid)

Invariant dimensionless split (eigenvalue difference of `A`, delta=0.01),
contrasted with the Article-H SIGNED mean (n=2, a0=33.7, xi=0.4):

| class | Article-H SIGNED chih_split | micro-pilot INVARIANT split |
|---|---|---|
| C4v | +2.805 | ~2.16 |
| Cs_axis | -0.460 | ~2.17 |
| C1 | -0.298 | ~2.81 |

Reading:
- The INVARIANT split is POSITIVE and O(1) for ALL placement classes and near
  the continuum disk benchmark (2.54) for the symmetric placements. The doublet
  genuinely opens with a continuum-like magnitude regardless of placement.
- The SIGNED observable equals the invariant only for `C4v`, where the
  symmetry-adapted `p_x/p_y` labels coincide with the continuum axes. For
  `Cs_axis` and `C1`, the baseline-energy-order labels are decorrelated from the
  continuum axes, and the SIGNED mean turns NEGATIVE while the invariant stays
  positive.
- Therefore the negative `C1`/`Cs_axis` signed mean is a LABEL-ORIENTATION
  artifact (the digital baseline doublet axes are rotated/decorrelated relative
  to the continuum axes), not a physical sign of the shape response.

## Answer to the central question

The negative C1 signed mean is admissible ONLY as an explicitly label-dependent
digital statistic (a branch-order / axis-decorrelation measure), NOT as a
self-standing physical shape response. Publishing it as "the doublet response is
negative / the levels attract" would be incorrect: the basis-invariant response
is positive and O(1).

Recommended PRIMARY quantities:
- continuum shape derivative: the unordered eigenvalue pair of `A` and the
  invariant split `|lambda_+ - lambda_-|` (compare to `j11^2/j01^2`);
- digital branch-decorrelation statistics: the signed observable and the
  identity/swap decomposition, explicitly labeled as digital/label-dependent;
- n=2 vs n=4 comparison: the invariant split distribution and its tails (both
  are basis-invariant), never the signed mean alone.

## Continuum-anchored basis (protocol section 6)

To make `p_x/p_y`-like labels meaningful even for generic `C1` placements, do
NOT use baseline energy order. Options, with assessment:

- Projected quadrupole operator `Q = x^2 - y^2` (and its partner `2xy`)
  restricted to the doublet, diagonalized: directly selects the continuum-like
  quadrupole axes; robust; the natural choice, since the deformation itself is a
  quadrupole. Basis stability high; degeneracy handled (2D projection); applies
  to `n=4` (the squircle doublet is still `E`-like); leakage controlled by the
  same subspace check. Recommended.
- Diagonalize the projected reflection `M_x` (used for `C4v`): exact only when
  the placement has that mirror; fails for generic `C1`. Diagnostic only.
- Procrustes / overlap alignment to continuum disk `p_x/p_y` modes: works but
  needs a continuum reference on each domain; heavier.
- Eigenvectors of the continuum Hadamard matrix: circular (requires the answer);
  use only as a cross-check.
- Basis-INDEPENDENT eigenvalues of `A`: no gauge ambiguity at all; this is the
  cleanest primary object and should anchor all physical claims. The quadrupole
  basis is only needed if one insists on reporting per-branch (`chih_+`,
  `chih_-`) numbers.

Do not pick a basis because it yields a pleasing sign; anchor physical claims on
the gauge-free invariants and use the quadrupole basis only for interpretation.

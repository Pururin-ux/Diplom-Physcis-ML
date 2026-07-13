# Common Hilbert space, embedding, and transport

Baseline and deformed Hamiltonians act on different spaces `l2(S_0)`,
`l2(S_delta)`. To compare them one must identify the two spaces. This document
records which choices are canonical and whether the response depends on them.

## Two separate embedding questions

1. Embedding of VECTORS (for overlaps). The canonical choice is the `l2(Z^2)`
   inclusion: zero-pad each eigenvector on sites absent from its own domain.
   This is an isometry onto its image and is unambiguous; overlaps
   `<psi_0 | phi_delta>` computed this way see only the intersection
   `S_0 ∩ S_delta` (each mode is zero outside its own domain). This part is
   canonical and not a source of ambiguity.

2. Embedding of the OPERATOR (to define `H_delta - H_0`). Here there is a real
   ambiguity: on sites in `S_0 \ S_delta` (removed) or `S_delta \ S_0` (added),
   the two Hamiltonians are simply not both defined. `H_delta - H_0` is NOT
   defined without a connecting operator identifying the spaces. Options:
   - large-barrier (hard-wall): sites outside the domain are FORBIDDEN
     (onsite -> +infinity), i.e. removed. This is the physically correct choice
     for a hard-wall billiard: a lattice point outside the domain is not an
     available orbital.
   - zero-extension: keep removed sites at onsite 0 (a decoupled orbital at
     `E+4 = 4`, i.e. at the band CENTER, far above the low-energy states). This
     is NOT physical for a hard-wall dot and, if used to build `H_delta^ambient`,
     injects a spurious `+4 * |mode weight on removed sites|` term.
   - partial-isometry / Kato transport: identify the doublet subspaces by the
     canonical geometric unitary (finite-difference form: the polar factor of
     the overlap). This avoids operator subtraction entirely.

## How the response sidesteps and re-introduces the ambiguity

The response matrix does NOT subtract full Hamiltonians. It compresses each
Hamiltonian to the fixed 2D baseline doublet basis and compares the 2x2
projected operators `B_delta, B_0`. This is well-defined ONCE the compression
rule is fixed:

- Large-barrier compression `Bexact = V0r^T (H_delta+4) V0r`, `V0r` = baseline
  doublet restricted to `S_delta` (dropping removed sites). This is the
  physically correct hard-wall choice and equals the `k -> infinity` limit of
  the multi-state `Bk = M_k D_k M_k^T`.
- Zero-extension would add `+4 * (baseline weight on removed sites)` to the
  diagonal, a large embedding artifact after division by small `delta`.

Therefore the eigenvalues of `A = (Bexact - B0)/delta` ARE well-defined, but
only relative to the stated large-barrier embedding and a chosen transport. The
validation (`transport_comparison.md`, `truncation_error_analysis.md`) measures
how much they move between the admissible choices (large-barrier compression,
two-state vs multi-state truncation, raw-M vs polar-Q transport). If they move
by an amount comparable to the claimed effect, the eigenvalues are NOT absolute
physical invariants and the construction is only a convention-dependent digital
statistic.

## Statement

`H_delta - H_0` is not defined without an identification of `l2(S_0)` and
`l2(S_delta)`. The projected response is defined given (i) the large-barrier
compression and (ii) a transport (Kato/polar), both literature-standard. The
resulting eigenvalues are convention-relative, not absolute invariants; any
report must name the convention. Whether they are stable across the admissible
conventions is an empirical question answered by the validation micro-pilot.

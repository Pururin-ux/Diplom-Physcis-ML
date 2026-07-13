# Correction record to Article-Ib (additive; old commits unchanged)

## C1. Fixed-mode compression is NOT the single "exact" endpoint truth

Article-Ib compared a two-state deformed-basis construction against the exact
large-barrier fixed-mode Rayleigh-Ritz compression and called the ~2x
disagreement a "truncation error". That framing was too strong. There are THREE
distinct, individually well-defined physical objects, answering different
questions, which need NOT agree under a finite boundary jump:

1. Relaxed endpoint spectrum: the actual eigenvalues of the NEW Hamiltonian
   after full eigenfunction relaxation, `E_j(S+)`. (Article-Ic primary object.)
2. Frozen-mode Rayleigh-Ritz response: the energy of the OLD baseline modes
   evaluated in the new domain, `<psi_0 | H+ | psi_0>`. (A diagnostic
   direct-perturbation mark.)
3. Transported-subspace representation: the new low-energy subspace expressed in
   a chosen old coordinate system (projector/principal-angle description).

Their differences are physically meaningful (1 vs 2 = eigenfunction relaxation
contribution; 3 = amount of mode reorganization), NOT "error relative to a
single truth". Article-Ic keeps them explicitly separate and takes the RELAXED
endpoint shift as canonical, because it needs no basis, transport, or common
space.

## C2. The Article-Ib multi-state reconstruction was incomplete

The `Bk` sum used deformed excited states `1..k` and EXCLUDED the deformed
ground state; it also truncated at k=32. It therefore did not represent the full
spectral resolution, and the claim "k=2,4,8,16,32 converge to exact compression"
is incomplete. The corrected completeness check (ground state included, full
spectral sum equals direct compression) is in
`full_spectral_reconstruction_check.md` and enforced by a test.

## C3. The Article-Ib event detector was incomplete

Events were detected via a change in `len(S)`. A SWAP event (one site added and
one removed at the same threshold, leaving `len(S)` unchanged) is a genuine
event and would have been missed. Article-Ic detects events by the set
inequality `S_i != S_{i-1}` and stores full `added`/`removed` site sets.

## C4. What remains established (unchanged)

- The fixed-`a` digital Hamiltonian is piecewise constant in `delta`; there is
  no ordinary smooth derivative at fixed `a`. (Article-Ib, stands.)
- The continuum disk benchmark `j11^2/j01^2 = 2.538734` is correct
  (derived + MFS-verified in Article-I). (stands)
- The Article-H signed negative C1 mean is a label-dependent quantity, not a
  gauge-invariant continuum slope. (stands)
- The Article-Ib traceless Frobenius `= split/sqrt(2)` correction stands.
- No large `64^2` run is permitted.

This record supersedes only the Article-Ib "single-truth truncation-error"
framing; the Article-Ib verdict (the 2x2 response matrix is not a
transport/construction-stable derivative) is unchanged and reinforced.

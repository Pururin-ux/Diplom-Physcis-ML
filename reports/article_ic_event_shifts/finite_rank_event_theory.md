# Finite-rank event theory (textbook tools)

The per-event spectral shift is a FINITE-RANK perturbation of the tight-binding
Hamiltonian. This is standard linear algebra / spectral graph theory; only the
DISTRIBUTION of the resulting marks could conceivably be new.

## One added site: bordered matrix and secular equation

Adding a site with onsite `eps=0` and hopping vector `b` (entries -1 to existing
neighbors) borders the old Hamiltonian:

  H_+ = [[ H_- , b ], [ b^T , eps ]].

The characteristic polynomial factorizes (Schur complement of the (2,2) block):

  det(lam I - H_+) = det(lam I - H_-) * ( lam - eps - b^T (lam I - H_-)^{-1} b ).

So the new eigenvalues away from the old ones are the roots of the secular
(self-energy) equation `lam - eps = Sigma(lam) := b^T (lam I - H_-)^{-1} b`.
`Sigma(lam) = sum_k |b^T psi_k^-|^2 / (lam - E_k^-)` is the resolvent
self-energy; its poles at the old eigenvalues force exactly one new eigenvalue
between consecutive old ones (interlacing).

## q added sites (bundle)

For an added block `C` (q x q) coupled by `B` (|S_-| x q):

  det(lam I - H_+) = det(lam I - H_-) * det[ lam I - C - B^T (lam I - H_-)^{-1} B ].

The new levels solve the q x q matrix secular equation with self-energy
`B^T (lam I - H_-)^{-1} B`. Removing sites is the inverse Schur relation (the old
domain is the bordered extension of the new one).

## Cauchy interlacing (added/removed site)

Removing a site gives a principal submatrix `H_-` of `H_+`; by Cauchy
interlacing `E_k(H_+) <= E_k(H_-) <= E_{k+1}(H_+)`. Adding a site is the reverse.
For a rank-`r` change (r sites / bonds), each eigenvalue moves within a window
bounded by `r` neighboring old eigenvalues; individual `dE_{j,e}` are bounded but
NOT sign-definite in general (a bundle can push a level either way depending on
the sign structure of `b` against the mode). The GROUND state shift under adding
a boundary site with negative hoppings is sign-definite (lowers E0) in the usual
Perron-Frobenius sense after the standard sign transform; excited-level shifts
are not.

## What is textbook vs what could be new

- The secular equation, Schur complement, self-energy, and Cauchy interlacing are
  TEXTBOOK (Horn-Johnson; Brouwer-Haemers; Krein spectral shift function). The
  per-event mechanism is fully explained by them.
- Only the STATISTICS of the marks `{eta_{g,e}}` over the boundary-event process
  -- specifically whether the eigenfunction-weighted self-energy carries
  structure beyond the bare geometric (lattice-point-discrepancy) event process
  -- is a candidate for new content, and only if `discrepancy_model_comparison.md`
  shows Model 1 (eigenfunction-weighted) beats Model 0 (bare counting)
  reproducibly. Schur complement itself is NOT presented as new.

## Predicted sign/structure checks (verified numerically in tests and the pilot)

- one-site secular equation reproduces the exact new eigenvalues (toy test);
- multi-site Schur complement matches exact block elimination (toy test);
- Cauchy interlacing holds for toy vertex add/remove (test);
- telescoping of `dE_{j,e}` over a placement equals the endpoint spectral change
  (test + `event_process_summary.csv`).

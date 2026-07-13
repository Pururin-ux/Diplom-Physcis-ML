# Article-Ib literature and textbook gate

Purpose: before any computation, determine whether the reconstructed 2x2
invariant response matrix is a mathematically canonical object or a
transport/truncation/embedding-dependent finite-difference construction.
Primary sources only.

Status legend: KNOWN TEXTBOOK RESULT | KNOWN LITERATURE RESULT |
KNOWN RESULT, NEW APPLICATION | POTENTIALLY NOVEL | NOVELTY NOT ESTABLISHED.

## Mandatory question

> Is there a canonical definition in the literature of a first-order response
> matrix for a binary digital domain whose site set changes discontinuously
> under deformation?

**Answer from the literature: No canonical first-order DERIVATIVE exists (the
operator is piecewise constant, see `piecewise_constant_operator.md`). What does
exist is a set of canonical tools for the finite-difference / transport version
— Kato spectral-projection transport, principal angles / CS decomposition,
finite-rank perturbation + Cauchy interlacing for site removal, and Mosco /
connecting-operator frameworks for varying Hilbert spaces. The "response matrix"
is therefore a KNOWN construction TYPE whose value is only defined once a
transport and an embedding are fixed. It is not a new invariant.**

## Mapping table

| Topic / our construction | Known result | Source | Status |
|---|---|---|---|
| Shape derivative of discrete/graph Laplacian | No smooth derivative for combinatorial changes; spectral perturbation is finite-rank | Chung, *Spectral Graph Theory* (AMS 1997); Brouwer-Haemers, *Spectra of Graphs* (Springer 2012) | KNOWN TEXTBOOK RESULT |
| Adding/removing a vertex or edge changes the spectrum | Finite-rank perturbation; interlacing bounds | Brouwer-Haemers (2012); Haemers, LAA 226-228 (1995) | KNOWN TEXTBOOK RESULT |
| Site removal = principal submatrix | Cauchy interlacing; Schur complement / Feshbach | Horn-Johnson, *Matrix Analysis*; Thune, arXiv:1609.01089 (used in our Article-F R8) | KNOWN TEXTBOOK RESULT |
| Domain perturbation of the Dirichlet Laplacian | Hadamard formula (continuum); needs regularity | Sokolowski-Zolesio (1992); Grinfeld, JOTA 145 (2010) | KNOWN TEXTBOOK RESULT |
| Canonical transport of a spectral subspace along a parameter | Kato geometric/parallel transport: unitary U(s) with U(s)P(0)=P(s)U(s) | Kato, *Perturbation Theory* (1966), and Kato 1950; Avron-Seiler-Yaffe, CMP 110 (1987); Simon on Kato arXiv:1710.06999 | KNOWN TEXTBOOK RESULT |
| Principal angles / canonical unitary between two eigenspaces | CS decomposition; principal angles; nearest orthogonal = polar factor of the overlap | Golub-Van Loan, *Matrix Computations*; Bjorck-Golub, Math. Comp. 27 (1973) | KNOWN TEXTBOOK RESULT |
| Polar / Procrustes alignment of eigenmodes | Orthogonal Procrustes solved by SVD; nearest orthogonal matrix Q=UV^T | Schonemann, Psychometrika 31 (1966); Golub-Van Loan | KNOWN TEXTBOOK RESULT |
| Derivative of a spectral projector | dP = -(sum) resolvent forms; well-defined for smooth families only | Kato (1966); Reed-Simon vol. IV | KNOWN TEXTBOOK RESULT |
| Changing-domain Hilbert spaces / pullback to a reference | Mosco convergence + connecting operators; varying Hilbert spaces | Mosco, JFA 123 (1994); Kuwae-Shioya, Comm. Anal. Geom. 11 (2003); Rosler-Stepanenko, Math. Comp. 93 (2024) | KNOWN LITERATURE RESULT |
| Pixelated / rough domain spectral convergence | Norm-resolvent / Mosco convergence to the Dirichlet Laplacian | Rosler-Stepanenko (2024); Bramble-Hubbard, SINUM 5 (1968) | KNOWN LITERATURE RESULT |
| Lattice-point (weighted) discrepancy | Translation-variable discrepancy; flat points / rational normals | Brandolini-Colzani-Gariboldi-Gigante-Travaglini, Rev. Mat. Iberoam. 36 (2020); Iosevich-Sawyer-Seeger (2007) | KNOWN LITERATURE RESULT |
| Our specific object: transported finite-difference 2x2 endpoint response of a jumping digital domain, fixed-xi double scaling | Not found as a named canonical object; assembles the above known tools | (no direct source) | NOVELTY NOT ESTABLISHED |

## Consequence for the construction

- The 2x2 response is well-defined ONLY relative to (i) a transport
  (Kato/polar) and (ii) an embedding/connecting operator (large-barrier vs
  zero-extension). These are literature-standard choices, not free artifacts,
  but the value depends on them, so the eigenvalues are NOT absolute physical
  invariants without stating the convention.
- The truncated `M diag(E1,E2) M^T` (deformed doublet only) is a rank-2
  approximation of the exact projected operator; it must be validated against
  the multi-state / exact compression (this is the standard spectral-projection
  compression, not a new construction).
- Because every ingredient is textbook, no novelty can be claimed for the
  construction itself. Novelty, if any, can only be in the fixed-xi digital
  STATISTICS, and only after a direct comparison to lattice-point discrepancy
  theory (`discrepancy_prediction.md`).

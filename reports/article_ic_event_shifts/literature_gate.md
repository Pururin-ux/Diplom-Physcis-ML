# Article-Ic literature and textbook gate

Purpose: before any computation, determine whether the canonical event-shift
object and the eigenfunction-weighted event statistics are already known.
Primary sources only.

Status legend: KNOWN TEXTBOOK RESULT | KNOWN LITERATURE RESULT |
KNOWN RESULT, NEW APPLICATION | POTENTIALLY NOVEL | NOVELTY NOT ESTABLISHED.

## Main literature question

> Has the DISTRIBUTION of low-eigenvalue spectral jumps, as a smooth boundary
> sequentially crosses lattice sites, been studied before, especially as an
> eigenfunction-weighted marked version of lattice-point discrepancy?

**Answer: every INGREDIENT is textbook/known — the per-event shift is a
finite-rank perturbation (Krein spectral shift / Schur secular equation /
Cauchy interlacing); the geometric event process is lattice-point discrepancy;
the eigenfunction weight is the boundary-deformation matrix element (Hadamard /
Barnett-Cohen-Heller). The specific COMBINATION (an eigenfunction-weighted
marked point process of digital boundary events for a lattice billiard) was NOT
found as a named studied object. Therefore the construction is at most
KNOWN RESULT, NEW APPLICATION, and any novelty is NOVELTY NOT ESTABLISHED until
the eigenfunction-weighted marks are shown to carry structure beyond the bare
(known) discrepancy + finite-rank predictions.**

## Mapping table

| Topic / our object | Known result | Source | Status |
|---|---|---|---|
| Cauchy interlacing on vertex add/remove | eigenvalues interlace under principal submatrix / bordering | Horn-Johnson, *Matrix Analysis*; Brouwer-Haemers, *Spectra of Graphs* (2012) | KNOWN TEXTBOOK RESULT |
| Vertex/edge perturbation spectral shifts | finite-rank spectral perturbation of graphs | Brouwer-Haemers (2012); Chung, *Spectral Graph Theory* (1997) | KNOWN TEXTBOOK RESULT |
| Rank-one / finite-rank perturbation theory | eigenvalue shift laws, monotonicity | Kato (1966); Bhatia, *Matrix Analysis* (1997) | KNOWN TEXTBOOK RESULT |
| Schur complement / Feshbach reduction | block elimination; used in our Article-F R8 | Horn-Johnson; Thune, arXiv:1609.01089 | KNOWN TEXTBOOK RESULT |
| Krein spectral shift function | canonical count of eigenvalue shift under trace-class / finite-rank perturbation; trace formula | Krein (1953); Birman-Yafaev reviews; Gesztesy et al., spectral shift + DtN (PMC6407858) | KNOWN LITERATURE RESULT |
| Secular equation for bordered matrices | `det(lam I - H+) = det(lam I - H-)[lam - eps - b^T (lam I - H-)^{-1} b]` | standard linear algebra; spectral graph theory | KNOWN TEXTBOOK RESULT |
| Graph surgery, vertex deletion | interlacing and eigenvalue bounds under deletion | Brouwer-Haemers; Cvetkovic-Doob-Sachs | KNOWN TEXTBOOK RESULT |
| Pendant / internal vertex eigenvalue variation | eigenvalue interlacing and shifts | spectral graph theory; PMC3559027 (Schur/tree interlacing) | KNOWN LITERATURE RESULT |
| Resolvent identity / low-rank update | Sherman-Morrison-Woodbury; resolvent formula | Golub-Van Loan; Kato | KNOWN TEXTBOOK RESULT |
| Discrete Dirichlet-to-Neumann map | DtN for graphs; SSF-DtN link | Gesztesy-Mitrea-Nichols-Teschl; PMC6407858 | KNOWN LITERATURE RESULT |
| Lattice-point discrepancy as translation point process | translation-variable discrepancy; flat points, rational normals | Brandolini-Colzani-Gariboldi-Gigante-Travaglini, Rev. Mat. Iberoam. 36 (2020); Kendall; Iosevich-Sawyer-Seeger (2007) | KNOWN LITERATURE RESULT |
| Marked / compound jump point processes | marked point process, compound Poisson, jump measure | Daley-Vere-Jones, *Point Processes* (2003) | KNOWN TEXTBOOK RESULT |
| Eigenfunction-weighted boundary sums (the "weight") | boundary-deformation matrix elements = Hadamard weight; boundary quasi-orthogonality | Barnett-Cohen-Heller, PRL 85, 1412 (2000), nlin/0003018; Hassell-Zelditch (boundary traces) | KNOWN LITERATURE RESULT |
| Spectral convergence of digital domains | Mosco / norm-resolvent convergence | Rosler-Stepanenko, Math. Comp. 93 (2024) | KNOWN LITERATURE RESULT |
| Event-resolved spectral statistics of a DIGITAL billiard (our marked process) | not found as a named object | (no direct source) | NOVELTY NOT ESTABLISHED |

## Reading

- The canonical event shift `E_j(S+) - E_j(S-)` is a finite-rank perturbation
  shift: exactly the Krein/Schur/interlacing setting. Its mechanism is textbook.
- The bare geometry of which sites cross is lattice-point discrepancy: known.
- The eigenfunction weight is the boundary-deformation matrix element: known.
- Hence, IF the eigenfunction-weighted marks add nothing beyond the bare
  (discrepancy + finite-rank) predictions, the whole object is KNOWN physics
  (outcome E2 / STOP). Only a demonstrated, reproducible eigenfunction-weighted
  structure NOT captured by bare counting could be a candidate (E3), and even
  then novelty stays NOT ESTABLISHED until independently audited. No claim of a
  "new physical effect" is permitted at this gate.

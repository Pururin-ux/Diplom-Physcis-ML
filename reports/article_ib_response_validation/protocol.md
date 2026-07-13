# Article-Ib frozen protocol: validation of the invariant digital response matrix

Status: publicly timestamped prospective protocol for a VALIDATION of an
already-constructed object (the Article-I 2x2 response matrix). Not a discovery
preregistration. Pushed to the remote as a standalone commit; SHA recorded
before any validation-result commit. Amendments only via dated addenda pushed
before the affected computation.

Branch `article-ib-invariant-response-validation` from Article-I HEAD `57ebd43`.
Article-I/H/G/F files are unchanged except an explicit `correction_record.md`
(the Frobenius-norm error) added additively.

Central question: is the reconstructed 2x2 invariant response matrix a correct,
transport-stable digital event-response observable, or is Article-I a
truncation/embedding-dependent construction? No 64^2, no wide distribution
pilot, no manuscript until this is answered.

## Definitions (frozen)

Domain S(delta) = {r in Z^2 : F(r,delta) <= 1}, area-preserving
a_x=a0/sqrt(1-delta), a_y=a0*sqrt(1-delta). Kinetic scale E+4.

Baseline doublet vectors psi_0 = (v1,v2) (indices 1,2 above the ground state);
deformed eigenpairs (E_{delta,k}, phi_k). Overlap matrix on the common site
space `M_k = <psi_0 | phi_{1..k}>` (2 x k). Constructions of the projected
deformed doublet Hamiltonian (in the baseline doublet basis, units E+4):

- Two-state truncation: `B2 = M_2 diag(E_{d,1}+4,E_{d,2}+4) M_2^T`.
- Multi-state: `Bk = M_k diag(E_{d,i}+4) M_k^T`, k in {4,8,16,32}.
- Exact large-barrier compression:
  `Bexact = V0r^T (H_delta+4) V0r`, V0r = baseline doublet restricted to
  S_delta (sites outside S_delta dropped = infinite barrier). Equivalently the
  k->infinity limit of Bk. This is the embedding-explicit reference.
- Polar-transported: with `M_2 = U Sigma W^T`, `Q = U W^T`;
  `BQ = Q diag(E_{d,1}+4,E_{d,2}+4) Q^T`.

Response matrices: `A_X = (B_X - B_0)/delta`, `B_0 = diag(E_{0,1}+4,E_{0,2}+4)`.
One-sided `A_+` uses +delta; symmetric `A_sym = (B(+delta)-B(-delta))/(2 delta)`
when S(-delta) is a valid domain.

Reported per placement/delta: full M, singular values, Q, B2, B4, B8, B16, B32,
Bexact, A_+, A_sym, eigenvalue pair, trace, determinant, invariant split
|lam2-lam1|, traceless Frobenius norm, principal-axis angle, added/removed
sites, event count.

## Frozen invariants and the Frobenius correction

For a traceless symmetric 2x2 with eigenvalues (-s/2,+s/2):
`||A_traceless||_F = |s|/sqrt(2)`. The disk-benchmark split s=2.538734 gives
`||A_traceless||_F = 1.79516`. The Article-I claim `= 2.5387` was wrong by
sqrt(2); recorded in `correction_record.md` and enforced by a test.

The split magnitude `lam_max - lam_min >= 0` is nonnegative by definition;
"the invariant response is positive" is therefore NOT a physical result. The
frozen primary reportables are: unordered eigenvalue pair, trace, determinant,
split magnitude, traceless norm, principal-axis direction, and the deviation
from the continuum slope pair.

## Frozen tolerances

- truncation converged: `||A_32 - A_exact||_F / ||A_exact||_F <= 0.02` AND
  `|split_2 - split_exact|/|split_exact| <= 0.05`.
- transport stable: eigenvalues of A_M, A_Q, and A_exact agree within 5% of the
  split magnitude, AND the sequential Kato-polar transport changes each
  eigenvalue by <= 5% of the split.
- benchmark approach (n=2, C4v only): report same-order / trending / consistent
  within stated discretization error / not converged; never "converges" on two
  sizes.

## Frozen grids (validation micro-pilot only)

n in {2,4}; sizes a0 in {24.3, 33.7, 48.2} (subset allowed); placements per
class: 2 C4v, 2 Cs_axis, 4 C1; delta in {+/-0.005, +/-0.01, +/-0.02};
dense event scans for 3-5 representative placements only.
Forbidden: 64^2, full placement grid, wide size series, new production run.

## Frozen outcomes (V1-V4) and stop/go (A-D)

V1 VALIDATED DIGITAL RESPONSE MATRIX: exact/multi-state/polar agree within
tolerance, transport-stable, small truncation error after /delta, sym/one-sided
consistent, controlled benchmark approach. (Not continuum novelty.)
V2 VALID ENDPOINT/EVENT STATISTIC, NOT A DERIVATIVE: reproducible, depends on
discrete events, no fixed-a derivative, transport controlled for an explicitly
defined digital statistic.
V3 CONSTRUCTION NOT ROBUST: truncation or transport or embedding changes the
eigenvalues substantially; Article-I invariant micro-pilot withdrawn.
V4 KNOWN DISCREPANCY EFFECT: statistic matches an existing quantitative
discrepancy prediction; no new mechanism.

Stop/go: A STOP (unstable or reduces to known discrepancy); B REDEFINE (valid
event statistic, not a derivative); C CONTINUE DIGITAL (validated and not
explained by existing theory); D RETURN TO CONTINUUM (new continuum quantity,
unlikely). Do not choose the favorable option.

## Rules

Literature gate precedes computation (done: `literature_gate.md`). No phrase
"Hadamard lattice derivative" for any lattice object unless explicitly marked
continuum. No 64^2, no broad production grid. All numeric claims reproducible
from `validation_rows.csv`.

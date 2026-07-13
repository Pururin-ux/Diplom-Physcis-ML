# Correction record (additive; old commits not rewritten)

## C1. Frobenius norm of the traceless response (factor sqrt(2))

For a traceless symmetric 2x2 matrix with eigenvalues `(-s/2, +s/2)`:
`||A_traceless||_F = sqrt((s/2)^2 + (s/2)^2) = |s|/sqrt(2)`.

For the continuum disk split `s = 2.538734`:
`||A_traceless||_F = 2.538734 / sqrt(2) = 1.795160`.

The Article-I documents (`disk_benchmark_derivation.md`,
`observable_invariance.md`) stated the traceless Frobenius norm `= 2.5387`,
which is wrong by a factor `sqrt(2)`. The correct value is `1.79516`. This is
recorded here and enforced by a test (`tests/test_article_ib_validation.py`);
the Article-I commit history is left unchanged, and the Article-I micro-pilot
CSV reported `A_traceless_norm_dimless = tl_norm/k0` numerically (that number is
`split/sqrt(2)` and is itself correct); only the PROSE claim "traceless norm =
split" was wrong.

## C2. "Positive invariant split" is not a physical result

`lambda_max(A) - lambda_min(A) >= 0` by definition. The Article-I phrasing
"the invariant response is positive" is therefore trivially true and is NOT an
independent physical finding. Superseded: report the unordered eigenvalue pair,
trace, determinant, split magnitude, traceless norm, principal-axis direction,
and the deviation from the continuum slope pair separately (see
`observable_invariance.md`, now read with this caveat).

## C3. Leakage metric bug in the validation script

`run_article_ib_validation.py` computed `leakage = 1 - sum(M[:, :2]^2)`, which
equals `1 - ||M2||_F^2 ~ 1 - 2 = -1` for near-orthogonal doublets; the printed
`leakage = -1.0` is a wrong-convention artifact and is NOT used in any
conclusion. The correct small-angle diagnostic is `sv_min(M2) ~ 0.999`, which is
reported and used.

## C4. The Article-I invariant micro-pilot construction is superseded

The Article-I micro-pilot built the response from `M2 diag(E_d,1,E_d,2) M2^T`
(deformed-doublet projection). Article-Ib shows this disagrees with the correct
fixed-mode Rayleigh-Ritz compression by ~2x (up to 5x) and is event-driven. The
Article-I invariant micro-pilot is therefore WITHDRAWN as a "response matrix /
shape-derivative" (see `final_verdict.md`, outcome V3). The Article-I files are
not edited; this record supersedes their invariant-matrix interpretation. The
Article-I CONTINUUM benchmark (`j11^2/j01^2`, MFS-verified) and the label-artifact
conclusion (signed C1 sign is a labeling artifact) are unaffected and stand.

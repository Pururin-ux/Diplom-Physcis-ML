# Truncation and construction-error analysis

## Constructions compared (dimensionless invariant split, delta=0.01)

Two families of construction give SYSTEMATICALLY DIFFERENT answers:

- Deformed-eigenbasis family (used by Article-I): two-state `B2`, multi-state
  `Bk` (k=4,8,16,32), polar `BQ`. These agree with each other within a few
  percent.
- Fixed-baseline-mode compression (the standard first-order Rayleigh-Ritz /
  Hellmann-Feynman object): `Bexact = V0r^T (H_d+4) V0r` (large-barrier), and
  its properly normalized form `G^{-1/2} Bexact G^{-1/2}` (lost weight ~1e-5, so
  normalization is negligible).

Representative splits:

| n | class | a0 | two-state | exact (Rayleigh-Ritz) |
|---|---|---|---|---|
| 2 | C4v (0,0) | 24.3 | 3.196 | 1.464 |
| 2 | C4v (0,0) | 33.7 | 0.976 | 0.547 |
| 2 | C4v (0.5,0.5) | 24.3 | 1.247 | 0.000 |
| 2 | C1 (0.31,0.17) | 33.7 | 2.387 | 1.150 |
| 4 | C1 (0.6875,0.75) | 33.7 | 2.227 | 0.424 |

## Quantitative failure

- Two-state vs exact relative error in the split: mean 45% (C4v), 95% (Cs_axis),
  161% (C1); max 118% / 209% / 460%. The frozen tolerance was 5%.
- Spread across {k32, exact, polar} constructions: mean 60-67%, max up to 153%.
- For C4v (0.5,0.5) the exact response is EXACTLY zero while the two-state gives
  1.247 — a qualitative, not just quantitative, disagreement.

## Why small subspace angle does NOT bound the error

`sv_min(M2) ~ 0.999` (small principal angle between baseline and deformed
doublets), so the naive "leakage is tiny" argument would suggest the two-state
truncation is accurate. It is not. Reasons:
- The two-state construction projects onto the DEFORMED doublet, which already
  encodes the deformed answer; it is not the first-order response of the FIXED
  baseline modes. The exact compression `<psi_0|(H_d+4)|psi_0>` is the correct
  first-order object, and it differs by ~2x.
- The omitted contribution is energy-weighted: even ~1e-3 spectral weight routed
  through the deformed ground state (E+4 ~ 6e-3) and higher states, divided by
  delta ~ 1e-2, gives an O(1) error in the response. The unweighted leakage is
  not a valid bound after division by delta, exactly as the protocol warned.
- (Implementation note: the two-state multi-state sum also excluded the deformed
  ground state; including all states and using `Bexact` is the complete object.
  The `leakage` column in `validation_rows.csv` used a wrong sign convention and
  is not used for any conclusion; see `correction_record.md`.)

## Conclusion

The reconstructed 2x2 response is NOT truncation/construction stable: the
two-state form used by Article-I overestimates the split by roughly a factor of
two (up to 5x) relative to the correct fixed-mode Rayleigh-Ritz compression, and
the two disagree qualitatively (including exact zeros). The construction fails
the frozen 5% tolerance by 1-2 orders of magnitude. This alone forces outcome
V3 for the Article-I invariant micro-pilot.

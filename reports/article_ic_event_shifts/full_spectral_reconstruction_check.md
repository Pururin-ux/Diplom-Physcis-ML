# Corrected full spectral reconstruction check (technical, Article-Ib fix)

This is a technical correction of the Article-Ib multi-state reconstruction
(which excluded the deformed ground state and truncated at k=32). It is not
primary physics.

## Identity

For the baseline doublet projector `P_0 = sum_{i in {1,2}} |psi_i^0><psi_i^0|`
and the new (deformed/large-barrier) Hamiltonian `H_+` with complete
eigenbasis `{(E_{k,+}, psi_{k,+})}` on the new site set,

  P_0 H_+ P_0 = sum_{k>=0} E_{k,+} P_0 |psi_{k,+}><psi_{k,+}| P_0,

where the sum runs over ALL states INCLUDING the ground state `k=0`. Restricting
the baseline modes to the new domain (large-barrier), this equals the direct
compression `V0r^T H_+ V0r`. The Article-Ib `Bk` sum used deformed states
`1..k` only (excluding `k=0`) and stopped at 32, so it did not reach this
identity; the claimed `k`-convergence was incomplete.

## What the corrected check shows

The completeness identity (ground state included, full spectral sum) equals the
direct matrix compression exactly on any finite system; this is verified on a
toy chain in `tests/test_article_ic_events.py`
(`test_completeness_includes_ground_state`). It confirms that the Article-Ib
"multi-state vs exact" gap was partly an artifact of the incomplete sum, and that
the CORRECT statement is simply: the fixed-mode compression (object B) and the
relaxed spectrum (object A) are DIFFERENT physical objects (see
`article_ib_correction_record.md`), not two truncations of one truth. This does
not change the Article-Ib verdict that the 2x2 response matrix is not a
transport/construction-stable derivative; it sharpens why.

# Spectral mark definitions and the three separated objects

All marks use the fixed baseline scale `K_ref = E_0(S(0))+4` (additive). None is
called a derivative.

## Primary relaxed marks (object A)

`eta_{j,e} = (E_j(S_e^+) - E_j(S_e^-)) / K_ref`, j=0,1,2,3;
`eta_{g,e} = (g(S_e^+)-g(S_e^-))/K_ref`, `g = E_2 - E_1`;
`eta_{c,e} = (c(S_e^+)-c(S_e^-))/K_ref`, `c = (E_1+E_2)/2`.
These are the full relaxed spectral response of the digital domain to the event.
Basis/transport/gauge independent (eigenvalues only).

## Frozen-mode marks (object B, diagnostic)

`frozen_mode_shift_j = <psi_j(S_e^-) | (H(S_e^+)+4) | psi_j(S_e^-)>_restricted -
(E_j(S_e^-)+4)`: the Rayleigh quotient of the OLD mode evaluated in the NEW
domain (large-barrier restriction). This is the direct first-order
(Hellmann-Feynman-like) contribution. The relaxation residual
`eta relaxation = dE_j - frozen_mode_shift_j` is the eigenfunction-reorganization
part. B is NOT "the truth" and A is not "an error"; they answer different
questions (see `article_ib_correction_record.md`).

## Subspace-rotation marks (object C)

`projector_distance = ||P(S_e^+) - P(S_e^-)||_F` and the two principal angles
between the low-energy doublet subspaces (embedded in the union site space). This
measures HOW MUCH the modes reorganize, independent of any labeling.

## Geometry marks (Model 0 inputs)

added/removed counts, net site change, changed-edge count (symmetric difference
of bond sets `B(S_e^+) triangle B(S_e^-)` -- NOT the old buggy `cut_bonds_count`),
event rank, max coherent row/column run, local boundary normal angle, flatness
proxy (distance of the normal from a lattice axis), axis-aligned flag, event type
(ADD_ONLY / REMOVE_ONLY / SWAP / MULTI_* / COHERENT_ROW / COHERENT_COLUMN).

## Eigenfunction-weighted marks (Model 1 inputs)

- `boundary_weight_mode_j = sum over changed sites of sum over their neighbors of
  |psi_j^-(neighbor)|^2` (boundary amplitude of the doublet modes at the event);
- `changed_bond_weight = sum over changed edges of (psi_2^- psi_2^- - psi_1^-
  psi_1^-)` (differential doublet matrix element);
- `schur_predictor = w_2 - w_1` (differential self-energy weight for the gap);
- resolvent self-energy `B^T (lam I - H_-)^{-1} B` (from
  `finite_rank_event_theory.md`).

The gate question (`discrepancy_model_comparison.md`): do the eigenfunction-
weighted marks predict `eta_{g,e}` substantially better than the bare geometry
(Model 0), under leave-one-placement-out evaluation? If not -> known discrepancy
physics (STOP).

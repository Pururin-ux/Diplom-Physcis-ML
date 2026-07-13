# Event geometry marks (Model 0 features)

Per event bundle, the following geometric marks are stored (from the BEFORE
state and the exact continuum boundary), forming the bare-counting Model 0. They
are the lattice-point-discrepancy features and carry NO eigenfunction
information.

- `added_count`, `removed_count`, `net_site_change`, `event_rank` (= added +
  removed).
- `changed_edge_count`: `|B(S_e^+) triangle B(S_e^-)|`, the true number of
  changed nearest-neighbor bonds (symmetric difference), replacing the buggy
  Article-G/H `cut_bonds_count`.
- `max_row_length`, `max_column_length`: longest connected run of changed sites
  sharing a lattice row / column (coherent-segment proxy).
- `local_normal_angle`: outward normal of the smooth superellipse boundary at the
  event location (analytic gradient of `F`); `flatness_proxy`: distance of that
  angle from the nearest lattice axis (0/90 deg); `axis_aligned_normal`: flag for
  near-axis normals (the rational-normal / flat-segment case of
  Brandolini et al.).
- `event_type`: ADD_ONLY / REMOVE_ONLY / SWAP / MULTI_ADD / MULTI_REMOVE /
  COHERENT_ROW / COHERENT_COLUMN.

Model 1 adds the eigenfunction-weighted marks defined in
`spectral_mark_definitions.md` (`boundary_weight_mode_j`, `changed_bond_weight`,
`schur_predictor`, resolvent self-energy). The discrepancy gate
(`discrepancy_model_comparison.md`) asks whether Model 1 predicts the spectral
marks `eta_{g,e}` substantially better than Model 0, leave-one-placement-out.

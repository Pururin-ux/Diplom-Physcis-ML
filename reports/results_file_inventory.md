# Results file inventory

This inventory is read-only. It records existing result files without regenerating or overwriting them.

| Path | Kind | Rows x columns | SHA-256 prefix | Role | Purpose | Likely generator | Thesis use | Notes |
|---|---:|---:|---:|---|---|---|---|---|
| `reports/ar_scaling_relative_deviation.csv` | csv | 28 x 4 | `4c6b436092daa205` | derived summary | Fixed-shape check of max relative deviation of (E0+4)a^2 over five a values for each (n, r_AR). | generation path not identified; derived from reports/physics_sanity_checks.csv | Chapter 3, conclusion, abstracts; figure used in Chapter 3 and defense slides. | CSV generation should be scripted in the publication branch. |
| `reports/assets/ar_scaling_relative_deviation.png` | png | - | `f4a046b6f7ac125d` | generated figure | Heatmap of fixed-shape max relative deviation for (E0+4)a^2. | notebooks/regenerate_thesis_figures_ru.py from reports/ar_scaling_relative_deviation.csv | Chapter 3 and defense slides. | - |
| `reports/assets/benchmark_rect_validation.png` | png | - | `a0e280f937ba788e` | generated/supporting file | purpose not explicitly mapped in this audit | generation path not identified | not referenced by thesis includegraphics or known appendix tables | not a known core frozen-thesis file |
| `reports/assets/circle_bessel_e0_check.png` | png | - | `96f7a74d20288ab9` | generated figure | Circular n=2, r_AR=1 Bessel scale check for E0. | notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 3. | - |
| `reports/assets/de1_a2_scaling_by_n.png` | png | - | `4167c81d02c651d1` | generated/supporting file | purpose not explicitly mapped in this audit | notebooks/07_physics_sanity_checks.ipynb | not referenced by thesis includegraphics or known appendix tables | not a known core frozen-thesis file |
| `reports/assets/de2_near_degeneracy_n2_ar1.png` | png | - | `6a4f2a6a42dd8d62` | generated figure | dE2 near-degeneracy diagnostic for n=2, r_AR=1. | notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 3. | - |
| `reports/assets/e0_kin_a2_scaling_by_n.png` | png | - | `554de01718a5fdfa` | generated figure | E_kin a^2 scaling by n. | notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 3. | - |
| `reports/assets/mlp_ablation_improvement_by_cell.png` | png | - | `c5f885de80dc899b` | generated figure | Step 08 relative MLP improvement by comparison cell. | notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/mlp_ablation_ridge_vs_mlp_physics_mae.png` | png | - | `fdee2bbffb5ae90d` | generated figure | Ridge MAE vs MLP+physics MAE. | notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/mlp_ablation_seed_stability.png` | png | - | `230eca27dc6cdade` | generated figure | Step 08 MLP seed-stability diagnostics. | notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/mlp_raw_vs_physics_features.png` | png | - | `4014cfb788066a37` | generated figure | MLP on raw geometry parameters vs MLP with physically motivated descriptors. | notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/nsites_area_ratio_by_n.png` | png | - | `6b591d4fc3e1b939` | generated figure | N_sites / analytic area diagnostic by n. | notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 3. | - |
| `reports/assets/ridge_e0_loao_abs_residual_vs_edge_error.png` | png | - | `a1ff2a9df33b1f6a` | generated figure | E0/LOAO Ridge absolute residuals vs edge discretization diagnostics. | notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/ridge_e0_loao_abs_residual_vs_macro_params.png` | png | - | `8d486a87a1d37b78` | generated figure | E0/LOAO Ridge absolute residuals vs smooth macro-parameters. | notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/ridge_predictor_collinearity_e0_loao.png` | png | - | `fac75a18f03abc70` | generated/supporting file | purpose not explicitly mapped in this audit | notebooks/09_residuals_vs_edge_discretization.ipynb | not referenced by thesis includegraphics or known appendix tables | not a known core frozen-thesis file |
| `reports/assets/ridge_residual_correlation_heatmap.png` | png | - | `2d9d2cb84fe7e01d` | generated figure | Residual-correlation heatmap. | notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/ridge_residual_dominance_by_n.png` | png | - | `591fa8a2a2047307` | generated figure | Residual-correlation dominance summary by n. | notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 5. | - |
| `reports/assets/sublattice_imbalance_summary.png` | png | - | `05ab9fd4300d46e8` | generated figure | Sublattice imbalance diagnostic summary. | notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV | Chapter 3. | - |
| `reports/department_progress_5min_ru.md` | md | - | `ed54c456296899ea` | progress-presentation support | Older department-progress material, not part of frozen thesis results. | generation path not identified | not used by frozen thesis | Candidate for archiving outside publication branch. |
| `reports/department_progress_5min_ru_notes.md` | md | - | `e92a137b95b22a8a` | progress-presentation support | Older department-progress material, not part of frozen thesis results. | generation path not identified | not used by frozen thesis | Candidate for archiving outside publication branch. |
| `reports/department_progress_5min_ru_v2_notes.md` | md | - | `96b1084bb28bf76d` | progress-presentation support | Older department-progress material, not part of frozen thesis results. | generation path not identified | not used by frozen thesis | Candidate for archiving outside publication branch. |
| `reports/department_progress_5min_speaker_notes_ru.md` | md | - | `bf867c2ea7d709db` | progress-presentation support | Older department-progress material, not part of frozen thesis results. | generation path not identified | not used by frozen thesis | Candidate for archiving outside publication branch. |
| `reports/full_code_physics_math_integrity_audit.md` | md | - | `bd7d6b2dd3752579` | audit report | Earlier broad physics/math/result-integrity audit. | manual audit | Not a frozen thesis input; post-cleanup evidence. | - |
| `reports/mlp_ablation_per_fold.csv` | csv | 2016 x 13 | `b7c866c12ee6866a` | generated result detail | Step 08 per-fold MAE/RMSE/MaxAE and MLP iteration details. | notebooks/08_tiny_mlp_ablation.ipynb | Appendix support; used to derive physical-scale MAE table. | - |
| `reports/mlp_ablation_seed_stability.csv` | csv | 48 x 16 | `aa0265fb8b2b82fd` | generated result summary | Step 08 seed-stability diagnostics for MLP initialization. | notebooks/08_tiny_mlp_ablation.ipynb | Chapter 5 and supporting figure. | - |
| `reports/mlp_ablation_summary.csv` | csv | 16 x 17 | `db46c1ceacd04176` | generated result summary | Step 08 16-cell Ridge vs MLP comparison summary. | notebooks/08_tiny_mlp_ablation.ipynb | Chapter 5 and Appendix B table. | - |
| `reports/model_error_physical_scale.csv` | csv | 16 x 8 | `c333e323aad7036d` | derived summary | Relative MAE normalization by E_kin for E0 and by dE1 for dE1. | generation path not identified; derived from mlp_ablation_summary/per-fold data | Chapter 5, Appendix B, abstracts, conclusion. | CSV generation should be scripted in the publication branch. |
| `reports/physics_sanity_checks.csv` | csv | 140 x 23 | `d72673e1a29001bd` | generated result and diagnostic summary | Step 07 physical sanity checks: E_kin, scaling, Bessel check, site count and sublattice diagnostics. | notebooks/07_physics_sanity_checks.ipynb | Chapter 3, Chapter 5, abstracts/conclusion; input to Step 09 and thesis figures. | - |
| `reports/reproducibility_audit.md` | md | - | `generated` | audit report | Post-thesis reproducibility and integrity audit for the computational pipeline. | scripts/audit_reproducibility.py | Not a frozen thesis input; post-thesis development support. | - |
| `reports/results_file_inventory.md` | md | - | `generated` | audit inventory | Inventory of report CSV/PNG/MD files, traceability, hashes and thesis usage. | scripts/audit_reproducibility.py | Not a frozen thesis input; post-thesis development support. | - |
| `reports/results_integrity_audit.md` | md | - | `2d410a0f5f37468c` | audit report | Integrity check for the eigenvalue validation cleanup. | manual audit | Not a frozen thesis input; post-cleanup evidence. | - |
| `reports/ridge_oof_point_residuals.csv` | csv | 560 x 21 | `74f117d961c90f14` | generated result detail | Step 09 out-of-fold Ridge predictions, residuals and point-level diagnostics. | notebooks/09_residuals_vs_edge_discretization.ipynb | Chapter 5 residual analysis figures and summaries. | - |
| `reports/ridge_residual_correlations.csv` | csv | 64 x 9 | `dcd72fd1187bca2e` | generated result summary | Step 09 Spearman residual correlations after duplicate predictor cleanup. | notebooks/09_residuals_vs_edge_discretization.ipynb | Chapter 5 residual analysis. | - |
| `reports/ridge_residual_hypothesis_summary.csv` | csv | 16 x 18 | `ff64124c868de17d` | generated result summary | Step 09 primary residual-hypothesis decision table. | notebooks/09_residuals_vs_edge_discretization.ipynb | Chapter 5 and conclusion. | - |
| `reports/ridge_residual_predictor_collinearity.csv` | csv | 96 x 10 | `d5662f366c2cdcdd` | generated result summary | Step 09 predictor collinearity matrix for residual diagnostics. | notebooks/09_residuals_vs_edge_discretization.ipynb | Residual-analysis support; not directly printed as a thesis table. | - |

## Thesis figure references

- `reports/assets/ar_scaling_relative_deviation.png`: present; used by thesis/chapters/03_dataset_and_validation.tex
- `reports/assets/circle_bessel_e0_check.png`: present; used by thesis/chapters/03_dataset_and_validation.tex
- `reports/assets/de2_near_degeneracy_n2_ar1.png`: present; used by thesis/chapters/03_dataset_and_validation.tex
- `reports/assets/e0_kin_a2_scaling_by_n.png`: present; used by thesis/chapters/03_dataset_and_validation.tex
- `reports/assets/mlp_ablation_improvement_by_cell.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/mlp_ablation_ridge_vs_mlp_physics_mae.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/mlp_ablation_seed_stability.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/mlp_raw_vs_physics_features.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/nsites_area_ratio_by_n.png`: present; used by thesis/chapters/03_dataset_and_validation.tex
- `reports/assets/ridge_e0_loao_abs_residual_vs_edge_error.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/ridge_e0_loao_abs_residual_vs_macro_params.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/ridge_residual_correlation_heatmap.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/ridge_residual_dominance_by_n.png`: present; used by thesis/chapters/05_results_and_discussion.tex
- `reports/assets/sublattice_imbalance_summary.png`: present; used by thesis/chapters/03_dataset_and_validation.tex

## Missing thesis-referenced files

None.

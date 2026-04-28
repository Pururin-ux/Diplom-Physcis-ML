# Full code, physics, and result-integrity audit

## Executive verdict

**PASS WITH MINOR ISSUES: only non-result-affecting issues found.**

No evidence was found that the stated physical problem is computed dishonestly, that the main spectra are taken from the wrong part of the band, that LOAO/LOARO validation leaks held-out groups, or that MLP/residual results are cherry-picked. The saved dense dataset and the generated report CSVs are internally consistent with the stated grid, target definitions, metrics, and decision rules.

The main issue is a validation/DRY weakness in `src/dataset.py::_superellipse_levels_and_site_count`: the primary superellipse dataset path validates eigenvalues by `np.sort(np.asarray(vals, dtype=float))` instead of reusing `src.kwant_solver._as_sorted_real_finite`. This does not by itself show that any reported number is wrong, but it is a real validation-safety issue and should be fixed with a dataset-equivalence check before final archival.

## Scope

Files and outputs inspected:

- `src/geometry.py`
- `src/kwant_solver.py`
- `src/baseline.py`
- `src/dataset.py`
- `src/model.py`
- `tests/test_dataset.py`
- `tests/test_kwant_solver.py`
- `tests/test_model_baselines.py`
- `tests/test_superellipse_dataset.py`
- `tests/test_superellipse_geometry.py`
- `notebooks/07_physics_sanity_checks.ipynb`
- `notebooks/08_tiny_mlp_ablation.ipynb`
- `notebooks/09_residuals_vs_edge_discretization.ipynb`
- `notebooks/regenerate_thesis_figures_ru.py`
- `data/superellipse_discrete_n_dense_dataset.npz`
- `reports/physics_sanity_checks.csv`
- `reports/mlp_ablation_summary.csv`
- `reports/mlp_ablation_per_fold.csv`
- `reports/mlp_ablation_seed_stability.csv`
- `reports/ridge_oof_point_residuals.csv`
- `reports/ridge_residual_correlations.csv`
- `reports/ridge_residual_predictor_collinearity.csv`
- `reports/ridge_residual_hypothesis_summary.csv`
- `reports/ar_scaling_relative_deviation.csv`
- `reports/model_error_physical_scale.csv`
- `METHODOLOGY_DECISIONS.md`
- thesis chapters and appendices were checked only for consistency with report numbers, not rewritten.

Commands/checks run:

- `rg` searches over source, tests, notebooks, methodology, thesis, and reports.
- Read-only NPZ/CSV consistency script using the `diplom-kwant` Conda environment.
- `python -m pytest tests -q` with default Python.
- `C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q`.

The audit did **not** rerun Kwant dataset generation, notebooks, report generation, or figure generation, in accordance with the task constraints.

## Physics correctness

### Tight-binding Hamiltonian and boundary conditions

Verdict: **OK.**

Evidence:

- `src/geometry.py` documents and constructs a square-lattice finite system with zero onsite energy and nearest-neighbor hopping `-1`.
- The geometry builders include only lattice sites inside the finite domain; no periodic wraparound or lead attachment was found. This corresponds to open finite-domain boundary conditions.
- `src/kwant_solver.py` extracts the Hamiltonian matrix of the finalized finite Kwant system and requests the smallest algebraic eigenvalues via `eigsh(..., which="SA")` for normal-size systems.

Possible concern:

- None result-affecting found.

### Rectangular control problem

Verdict: **OK.**

Evidence:

- `src/baseline.py::exact_rectangular_tb_levels` uses the open-boundary separable spectrum
  `E_mn = -2 t [cos(pi m/(Nx+1)) + cos(pi n/(Ny+1))]`
  with indices starting at 1. This matches the stated finite open-chain convention for hopping `-t`.
- Tests check normal rectangular energy ordering and square-case degeneracy.

Possible concern:

- No direct issue. More exhaustive comparison between rectangular Kwant spectra and the analytic formula is useful but not required to trust the current reported checks.

### Superellipse geometry

Verdict: **OK.**

Evidence:

- `src/geometry.py::build_superellipse_dot` includes lattice sites satisfying
  `abs(x / a)**n + abs(y / b)**n <= 1.0`.
- The saved dense dataset contains `b = a * aspect_ratio` consistently through the grid used in reports.
- The reported diagnostic area is consistent with the superellipse analytic area formula to floating-point precision; the maximum recomputed area discrepancy in `reports/physics_sanity_checks.csv` was at numerical roundoff scale.

Possible concern:

- The superellipse is centered on the integer lattice origin. This is a modeling convention, not an error; it should remain stated as a finite lattice-domain convention.

### Energy ordering and band bottom

Verdict: **OK, with one validation-safety concern in the superellipse path.**

Evidence:

- `src/kwant_solver.py::lowest_four_energies` sorts eigenvalues and validates that they are real and finite via `_as_sorted_real_finite`.
- `src/dataset.py::_superellipse_levels_and_site_count` uses `eigsh(..., which="SA")`, so it asks for the lowest algebraic eigenvalues, i.e. the bottom of the square-lattice band, not high-energy states.
- In the saved dense dataset:
  - `E0` ranges from `-3.996132993965974` to `-3.978659036696258`.
  - `E0 + 4` ranges from `0.0038670060340257884` to `0.021340963303742022`.
  - This is consistent with low-energy states near the band bottom `E = -4`.

Possible concern:

- `src/dataset.py::_superellipse_levels_and_site_count` bypasses `_as_sorted_real_finite` and instead casts/sorts inline. A complex-valued or non-finite solver result would not be rejected by the same validation used in `src/kwant_solver.py`. This is a validation-safety issue, not evidence of an incorrect saved result.

### Spectral targets and gaps

Verdict: **OK.**

Evidence:

- The saved dense dataset has gap definitions exactly consistent with eigenvalues:
  - max `|dE1 - (E1 - E0)| = 0.0`
  - max `|dE2 - (E2 - E1)| = 0.0`
  - max `|dE3 - (E3 - E2)| = 0.0`
- `METHODOLOGY_DECISIONS.md` documents the convention `E_kin = E0 + 4`, the dE2 diagnostic-only decision, and the physical sanity checks before MLP.

Possible concern:

- No result-affecting concern.

### Boundary-discretization diagnostics

Verdict: **OK.**

Evidence:

- `reports/physics_sanity_checks.csv` is exactly consistent with the dense NPZ for `N_sites`, `E0`-`E3`, and `dE1`-`dE3`.
- `N_sites / analytic_area` ranges from `0.9809385181000999` to `1.0076065912754`, matching thesis/report statements.
- The maximum sublattice imbalance ratio is `0.02162565249813572`, at `n=1.2`, `a=24.0`, `aspect_ratio=1.0`.
- In step 09 outputs, `abs_delta_N_over_N` remains in point residuals as an alias, but is excluded from residual ranking and collinearity tables. The final predictor set is exactly `a`, `aspect_ratio`, `edge_area_error_abs`, `imbalance_ratio`.

Possible concern:

- None after the duplicate-predictor cleanup. The alias is correctly not treated as an independent predictor in the final correlation ranking.

## Mathematical correctness

### Feature matrices

Verdict: **OK.**

Evidence:

- `src/model.py::make_ablation_feature_matrix(..., feature_set="raw")` returns `[a, aspect_ratio]`.
- `src/model.py::make_ablation_feature_matrix(..., feature_set="physics_informed")` returns `[1/a^2, 1/(a^2 * aspect_ratio), aspect_ratio]`.
- Tests verify the ablation feature matrix values and reject nonpositive `a` or nonpositive aspect ratio.

Possible concern:

- No mathematical error found. The feature basis is physically motivated but not unique, which is already documented in the thesis.

### Metrics and improvement formulas

Verdict: **OK.**

Evidence from recomputation of saved CSVs:

- `reports/mlp_ablation_summary.csv` has 16 rows, one per `(n, target, protocol)` cell.
- The improvement formula recomputes as
  `(ridge_mae - mlp_physics_mae_mean) / ridge_mae * 100`
  with maximum numerical discrepancy `2.842170943040401e-14`.
- The seed-stability formula recomputes exactly:
  `delta_mae > 0 and delta_mae > 2 * mlp_physics_mae_se`.
- The `cell_success` rule recomputes exactly:
  `passes_15_percent and seed_stable and not has_convergence_failures`.
- All convergence-failure counts in the summary are zero.

Possible concern:

- None.

### AR fixed-shape scaling check

Verdict: **OK.**

Evidence:

- `reports/ar_scaling_relative_deviation.csv` has 28 rows, one for each fixed `(n, r_AR)` slice.
- The maximum fixed-shape relative deviation is `2.117041397693207%` at `n=4.0`, `r_AR=0.72`.
- This matches the intended check: `Q(a) = (E0 + 4) a^2`, mean over the five `a` values, and maximum relative deviation from that mean.

Possible concern:

- None.

### Physical-scale MAE normalization

Verdict: **OK.**

Evidence:

- `reports/model_error_physical_scale.csv` has 16 rows.
- For `E0`, characteristic scale is computed from `E0 + 4`, not from `|E0|`.
- For `dE1`, characteristic scale is computed from `dE1`.
- Relative MAE ranges:
  - Ridge, `E0`: `2.00871627789%` to `2.60282378818%`.
  - Ridge, `dE1`: `0.782125713345%` to `1.14715140302%`.
  - MLP+physics, `E0`: `0.508142794438%` to `2.06329383973%`.
  - MLP+physics, `dE1`: `0.485814988635%` to `3.30555736477%`.

Possible concern:

- None.

### Residual correlations

Verdict: **OK.**

Evidence:

- `reports/ridge_oof_point_residuals.csv` has 560 rows: 4 `n` classes x 2 targets x 2 protocols x 35 held-out points.
- `residual = y_pred - y_true`, `abs_residual = abs(residual)`, and `squared_residual = residual^2` recompute exactly from the saved point-level file.
- `reports/ridge_residual_correlations.csv` has 64 rows and uses only variables `a`, `aspect_ratio`, `edge_area_error_abs`, and `imbalance_ratio`.
- `reports/ridge_residual_predictor_collinearity.csv` has 96 rows; each target/protocol/n subset has 6 predictor-pair rows, as expected for four predictors.
- The primary hypothesis summary reports `primary_hypothesis_supported = False`; meaningful discretization support appears in 1 of 4 primary `E0`/LOAO classes.
- The `n=1.2` primary diagnostic correlation remains:
  `rho = -0.415686274509804`, `|rho| = 0.415686274509804`, `p = 0.013011328456051107`.

Possible concern:

- Spearman correlations are diagnostic associations, not causal tests. The thesis wording already treats them cautiously.

## Dataset integrity

Verdict: **OK.**

Dense dataset checked: `data/superellipse_discrete_n_dense_dataset.npz`.

Grid:

- Row count: 140.
- `a`: `[24.0, 27.0, 30.0, 33.0, 36.0]`.
- `aspect_ratio`: `[0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0]`.
- `n`: `[1.2, 2.0, 3.0, 4.0]`.
- Duplicate `(n, a, aspect_ratio)` rows: 0.
- Expected grid size `4 x 5 x 7 = 140`: confirmed.

Saved report consistency:

- `reports/physics_sanity_checks.csv` matches the NPZ exactly for `N_sites`, `E0`-`E3`, and `dE1`-`dE3`.
- No silent target mismatch was found in the saved physics sanity report.

CSV row counts and short SHA-256 prefixes:

- `reports/physics_sanity_checks.csv`: 140 rows, `d72673e1a290`.
- `reports/mlp_ablation_summary.csv`: 16 rows, `db46c1ceacd0`.
- `reports/mlp_ablation_per_fold.csv`: 2016 rows, `b7c866c12ee6`.
- `reports/mlp_ablation_seed_stability.csv`: 48 rows, `aa0265fb8b2b`.
- `reports/ridge_oof_point_residuals.csv`: 560 rows, `74f117d961c9`.
- `reports/ridge_residual_correlations.csv`: 64 rows, `dcd72fd1187b`.
- `reports/ridge_residual_predictor_collinearity.csv`: 96 rows, `d5662f366c2c`.
- `reports/ridge_residual_hypothesis_summary.csv`: 16 rows, `ff64124c868d`.
- `reports/ar_scaling_relative_deviation.csv`: 28 rows, `4c6b436092da`.
- `reports/model_error_physical_scale.csv`: 16 rows, `c333e323aad7`.

Limit of this audit:

- The dense spectra were not regenerated from Kwant because the task explicitly forbids rerunning dataset generation. Therefore this audit verifies internal consistency and code-path plausibility, not an independent fresh recomputation of all 140 spectra.

## Validation and leakage audit

Verdict: **No leakage found.**

Evidence:

- `src/model.py::evaluate_leave_one_group_out` creates a fresh model inside each group fold using `build_baseline_model`.
- The fold split is by exact group value:
  - LOAO groups by `a`.
  - LOARO groups by `aspect_ratio`.
- Training masks exclude the entire held-out group.
- `StandardScaler` appears inside the model pipeline or `TransformedTargetRegressor`, so it is fitted only during `model.fit` on training rows for that fold.
- Notebook 08 uses a model factory and constructs a new Ridge or MLP instance for each fold/seed combination.
- Notebook 09 point-level residuals fit a fresh physics-informed Ridge model for each left-out group and store predictions only for held-out geometries.

Reproducibility:

- MLP configuration is fixed and seed-stability is evaluated over the saved seed set. No hyperparameter search or seed-picking was found.

Possible concern:

- No data leakage was found. The main reproducibility weakness is that final Russian-labeled figures are regenerated by `notebooks/regenerate_thesis_figures_ru.py`, while some older notebooks still contain earlier English plot labels. Rerunning the older notebooks could overwrite final presentation figures, but not the numeric CSV results.

## Result integrity / no-manipulation audit

Verdict: **No evidence of post-hoc filtering, cherry-picking, or hidden exclusion.**

Evidence:

- `METHODOLOGY_DECISIONS.md` documents before-result decisions for:
  - energy convention;
  - physical sanity checks;
  - Bessel/circle benchmark threshold;
  - dE2 diagnostic-only status;
  - fixed discrete `n` classes;
  - MLP as an ablation/control experiment;
  - MLP hidden layer size `(4,)`;
  - structured LOAO/LOARO validation;
  - 15% practical improvement criterion;
  - seed-stability criterion;
  - Ridge remaining preferred if the criterion is not met;
  - residual analysis against edge-discretization quantities.
- `reports/mlp_ablation_summary.csv` includes all 16 cells. Negative MLP results are retained, including all four `dE1`/LOAO losses.
- No convergence-failed folds are present in the main comparison; the convergence columns are still recorded.
- The MLP final decision is determined by the recorded formula, not by selecting the best-looking protocol.
- The residual analysis includes all target/protocol/n combinations and clearly labels the primary hypothesis as not supported.
- The duplicate predictor `abs_delta_N_over_N` was removed from residual ranking and collinearity, while retained only as an alias in point residuals.

Possible concern:

- None result-affecting.

## Report and thesis-number consistency

Verdict: **Mostly consistent; one wording issue needs correction.**

Checked numbers that match saved reports:

- Dense superellipse grid: 140 geometries.
- `n = {1.2, 2.0, 3.0, 4.0}`.
- `a = {24, 27, 30, 33, 36}`.
- `aspect_ratio = {0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0}`.
- Bessel/circle relative error stated as about `2.03%`.
- Fixed-shape AR scaling maximum relative deviation stated as about `2.12%`.
- `N_sites / analytic_area` range matches `0.9809385181000999` to `1.0076065912754`.
- Maximum imbalance ratio matches about `2.16%`.
- MLP+physics success cells: `10/16`.
- LOAO successes: `3/8`.
- LOARO successes: `7/8`.
- MLP+physics better than MLP raw: `13/16`.
- Average MLP raw MAE: about `1.6067e-4`.
- Average MLP+physics MAE: about `1.4215e-4`.
- Largest MLP+physics improvement: `80.47724948785128%` for `n=2.0`, `E0`, LOARO.
- Worst MLP+physics improvement: `-236.37349873674813%` for `n=3.0`, `dE1`, LOAO.
- `dE1`/LOAO improvements:
  - `n=1.2`: `-115.44292140791542%`;
  - `n=2.0`: `-157.88478209124628%`;
  - `n=3.0`: `-236.37349873674813%`;
  - `n=4.0`: `-203.65467068857888%`.
- Primary residual hypothesis: not supported.
- Primary meaningful/diagnostic discretization support: `1/4`.
- Primary `n=1.2` imbalance signal: `rho = -0.415686274509804`, `p = 0.013011328456051107`.
- Physical-scale relative MAE ranges match `reports/model_error_physical_scale.csv`.

Wording mismatch:

- `thesis/chapters/05_results_and_discussion.tex` states that for `E0` under LOAO, MLP with physical features improves Ridge in `3 of 4` `n` classes. The CSV shows positive MAE improvement in all 4 `E0`/LOAO classes, but only 3 of 4 satisfy the success criterion because the `n=4.0` improvement is `1.94%`, below the 15% threshold. Recommended wording: "criterion-successful/practically significant improvement in 3 of 4", or "formal MAE reduction in 4 of 4, with the pre-registered success criterion met in 3 of 4."

This is a thesis wording issue, not a numerical result change.

## Code quality findings

### Finding 1

- Severity: **2 = validation safety**
- File/function: `src/dataset.py::_superellipse_levels_and_site_count`
- Description: The primary superellipse dataset path calls `eigsh`/`eigvalsh` directly and then validates by `np.sort(np.asarray(vals, dtype=float))`. This bypasses `src.kwant_solver._as_sorted_real_finite`, which checks real-valued and finite eigenvalues. A complex or non-finite solver result could be silently cast or handled inconsistently.
- Recommended fix: Import and call `_as_sorted_real_finite(vals)` after `eigsh`/`eigvalsh`, or expose a public geometry-generic validation helper from `src.kwant_solver.py`.
- Requires rerun: The code fix itself should not change valid spectra, but after the fix the dense grid should be recomputed in memory and compared against the saved NPZ before any report/thesis updates. If arrays are unchanged, no downstream rerun is needed.

### Finding 2

- Severity: **1 = maintainability**
- File/function: `tests/test_kwant_solver.py`, `tests/test_superellipse_dataset.py`
- Description: Tests cover rectangular eigenvalue behavior and mocked superellipse dataset generation, but there is no direct unit test for `_as_sorted_real_finite`, and the real `_superellipse_levels_and_site_count` path is not directly tested on a representative small/medium superellipse.
- Recommended fix: Add tests that `_as_sorted_real_finite` sorts finite real values and rejects complex/non-finite values; add a dataset-level test that `_superellipse_levels_and_site_count` returns four finite sorted energies for a representative geometry.
- Requires rerun: Tests only. No scientific rerun unless the tests expose changed numerical behavior.

### Finding 3

- Severity: **1 = maintainability/reproducibility**
- File/function: `notebooks/07_physics_sanity_checks.ipynb`, `notebooks/08_tiny_mlp_ablation.ipynb`, `notebooks/09_residuals_vs_edge_discretization.ipynb`
- Description: Some notebook plotting cells still contain older English labels/titles, while final thesis figures were regenerated through a separate Russian-label script. Rerunning old notebooks after the figure-label cleanup may overwrite presentation PNGs with outdated labels.
- Recommended fix: Either update notebook plotting cells to the same Russian labeling policy as `notebooks/regenerate_thesis_figures_ru.py`, or document that the figure-regeneration script is authoritative for final thesis figures.
- Requires rerun: Figure-only rerun if labels are synchronized; no data or result rerun.

### Finding 4

- Severity: **1 = report wording consistency**
- File/function: `thesis/chapters/05_results_and_discussion.tex`
- Description: The `E0`/LOAO statement says "improves in 3 of 4", while the numeric CSV has positive MAE improvement in 4 of 4 and criterion success in 3 of 4. This can confuse "positive improvement" with "pre-registered success."
- Recommended fix: Clarify the wording as described in the report consistency section.
- Requires rerun: No.

### Finding 5

- Severity: **1 = environment reproducibility**
- File/function: environment/tooling
- Description: In the current PowerShell session, default `python` lacks `pytest`, and `conda` is not on PATH. Tests pass using the explicit Miniforge path: `C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q`.
- Recommended fix: Document the explicit Conda/Miniforge activation command or ensure Conda is on PATH in the development shell.
- Requires rerun: No scientific rerun.

## Test results

Default Python:

```text
python -m pytest tests -q
C:\Users\lalad\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe: No module named pytest
```

Conda environment:

```text
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q
30 passed, 1 warning in 2.85s
```

The warning is the existing OpenMP/threadpool warning about Intel OpenMP and LLVM OpenMP both being loaded. It did not cause test failure.

## Required actions before final PDF

1. Fix the superellipse eigenvalue-validation path in `src/dataset.py::_superellipse_levels_and_site_count` to reuse `_as_sorted_real_finite`, then run tests and compare fixed-code dense-grid outputs against `data/superellipse_discrete_n_dense_dataset.npz` before deciding whether any reports need rerun.
2. Clarify the Chapter 5 wording around `E0`/LOAO: distinguish formal positive MAE improvement in 4 of 4 classes from pre-registered criterion success in 3 of 4 classes.
3. Avoid rerunning older notebooks over final thesis figures unless their plot labels are synchronized with the Russian-label regeneration script.

No current thesis numerical conclusion appears to require change based on this audit.

## Optional actions after defense

1. Replace the private helper import plan with a public geometry-generic eigenvalue validation helper, e.g. `validate_lowest_eigenvalues`.
2. Add a small manifest recording hashes of final NPZ/CSV report files and final PNG figures.
3. Consolidate plot generation so notebooks and thesis figure scripts cannot diverge.
4. Add a lightweight "audit" command or notebook that recomputes the CSV consistency checks used here.
5. Archive or clearly label legacy pilot notebooks that contain older inline eigensolver logic.


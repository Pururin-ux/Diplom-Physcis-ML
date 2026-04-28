# Diploma Physics ML

This repository contains the code, notebooks, reports, and thesis draft for a
physics diploma project on conservative surrogate approximation of low-energy
spectra of model quantum dots computed with Kwant.

## Current status

The main superellipse workflow is complete through:

- Stage 07: physical sanity checks.
- Stage 08: tiny MLP ablation/control experiment.
- Stage 09: Ridge residual analysis against edge-discretization diagnostics.

The LaTeX thesis draft/PDF scaffold is assembled under `thesis/`.

The current dense superellipse dataset contains 140 geometries:

- `n = {1.2, 2.0, 3.0, 4.0}`
- `a = {24, 27, 30, 33, 36}`
- `aspect_ratio = {0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0}`

Main generated reports and audit outputs are in `reports/`.

## Scientific conclusion

Within the verified parameter range, the low-energy spectra are largely
captured by physically motivated confinement descriptors. The
physics-informed Ridge model remains the preferred surrogate: it is simpler,
stable, interpretable, and physically grounded.

The small MLP ablation does not meet the pre-registered robust-success
criterion. It improves some cells, especially for `E0` and LOARO, but it does
not provide a robust advantage over physics-informed Ridge under structured
LOAO/LOARO validation.

The residual analysis does not support a global claim that simple
edge-discretization diagnostics explain the remaining Ridge residuals.

## Scope

The project uses:

- square-lattice tight-binding Hamiltonians with onsite energy `0` and
  nearest-neighbor hopping `-1`;
- direct Kwant calculations as the reference spectra;
- fixed discrete-`n` superellipse quantum dots as the main geometry family;
- `E0` and `dE1 = E1 - E0` as the main targets;
- `dE2` only as a diagnostic quantity because of degeneracy and level-ordering
  sensitivity.

The rectangular quantum dot is used only as a validation/control calculation,
not as the main research object.

## Repository structure

- `src/` - reusable Python code.
- `notebooks/` - executed analysis notebooks.
- `tests/` - unit and sanity tests.
- `data/` - generated datasets.
- `reports/` - CSV reports, plots, and integrity audits.
- `thesis/` - LaTeX thesis draft and build files.

## Reproducibility

Tests pass in the `diplom-kwant` environment:

```powershell
conda run -n diplom-kwant python -m pytest tests -q
```

Current result: `30 passed` in the configured environment.

If `conda` is not on `PATH` on Windows, use the local Miniforge/Conda path or
activate the environment manually before running the command.

## Not completed / future work

The following are future extensions, not completed thesis results:

- inverse design or inverse geometry search;
- DFT/OpenMX or other material-specific calibration;
- continuous-`n` generalization;
- arbitrary-shape generalization;
- claims that a surrogate replaces direct Kwant calculation.

The project should be interpreted as a controlled model-nanostructure study,
not as a material-specific prediction pipeline.

# Diploma Physics ML

Code, notebooks, tests, reports and thesis materials for my diploma project on low-energy spectra of model quantum dots.

The reference spectra are calculated directly with Kwant. A simple physics-informed Ridge model is used as a surrogate and compared with a small MLP under structured holdout tests. In the tested parameter range, the Ridge model was more stable and easier to interpret, so it remained the main surrogate.

## What is in the repository

- `src/` — Python code used by the analysis pipeline
- `notebooks/` — executed analysis notebooks
- `tests/` — unit and physical sanity checks
- `data/` — generated datasets
- `reports/` — tables, plots and audit outputs
- `thesis/` — LaTeX thesis sources

## Dataset

The main superellipse dataset contains 140 geometries:

- `n = {1.2, 2.0, 3.0, 4.0}`
- `a = {24, 27, 30, 33, 36}`
- `aspect_ratio = {0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0}`

The model uses square-lattice tight-binding Hamiltonians with onsite energy `0` and nearest-neighbor hopping `-1`. The main targets are `E0` and `dE1 = E1 - E0`. `dE2` is kept only as a diagnostic quantity because of degeneracy and level-ordering sensitivity.

## Main result

Within the verified parameter range, low-energy spectra are captured well by physically motivated confinement descriptors. The small MLP did not show a robust advantage over the Ridge model under the structured validation used in the project.

The surrogate is not treated as a replacement for direct Kwant calculations. It is a compact approximation for this controlled model system.

## Reproducibility

Run the tests in the configured environment:

```powershell
conda run -n diplom-kwant python -m pytest tests -q
```

Current repository state: 30 tests pass in the configured environment.

## Scope

This is a model-nanostructure study. Material-specific DFT calibration, inverse geometry search, continuous-`n` generalisation and arbitrary-shape generalisation are outside the completed diploma work.

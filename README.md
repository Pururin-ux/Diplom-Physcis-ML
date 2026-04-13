# Diploma Physics ML

This project is a diploma prototype for building a surrogate machine learning model
that predicts the first low-energy levels of a simple 2D rectangular quantum dot
computed with Kwant.

## Project goal

The goal is to compare direct numerical calculation in Kwant with simple surrogate models
that predict the first 4 eigenenergies of the system from geometric parameters.

## Scope

This project is intentionally narrow and minimal.

We study:
- a simple closed 2D rectangular quantum dot,
- a square-lattice tight-binding model in Kwant,
- 2 input parameters: `Lx` and `Ly`,
- 4 output energy levels: `E0`, `E1`, `E2`, `E3`.

Preferred output encoding:
- `E0`
- `Δ1 = E1 - E0`
- `Δ2 = E2 - E1`
- `Δ3 = E3 - E2`

We do not include:
- full density of states (DOS),
- inverse design,
- PINNs,
- transformers,
- CNN/ResNet,
- HDF5/Dask,
- complex MLOps infrastructure.

## Main idea

The project has three possible model levels:

1. Analytical baseline  
2. Direct surrogate model  
3. Residual surrogate model

The direct surrogate is the main minimal ML target.

The residual surrogate is an optional research extension:
it learns the correction between the analytical baseline and the Kwant result.
It should only be kept if it improves performance over both:
- the analytical baseline,
- the direct surrogate model.

## Repository structure

- `src/` — core reusable Python code
- `notebooks/` — exploratory and presentation notebooks
- `tests/` — tests and sanity checks
- `data/` — generated datasets
- `models/` — saved surrogate models or artifacts

## Physics setup

Default physical setup:
- closed 2D rectangular quantum dot,
- square lattice,
- tight-binding Hamiltonian,
- first 4 low-energy eigenvalues only.

Current energy/sign convention in code:
- onsite energy is `0`,
- nearest-neighbor hopping is `-1`,
- low-energy levels correspond to the smallest algebraic eigenvalues (`which='SA'`).
- for square-like geometries (`Lx == Ly`), equal or nearly equal level pairs are expected from symmetry (degeneracy / near-degeneracy).

Default dataset setup:
- regular grid over `Lx` and `Ly`,
- default size: `20 x 20 = 400` configurations,
- default range: `Lx, Ly in [10, 30]` lattice units.

## First milestone

The first milestone is:
- implement a simple rectangular quantum dot in Kwant,
- compute the first 4 eigenenergies,
- verify physical sanity checks,
- create one notebook with basic parameter sweeps.

## Sanity checks

The generated spectra should satisfy:
- energies are finite real numbers,
- energies are sorted in nondecreasing order,
- no NaN or Inf values,
- energies change when `Lx` or `Ly` changes,
- when both `Lx` and `Ly` increase together, low-energy levels generally decrease,
- repeated calculations with the same parameters reproduce the same result.

## Metrics

The project should evaluate model quality using:
- MAE or RMSE for the energy levels,
- relative error in percent,
- error relative to the characteristic level spacing.

The preferred comparison is:
- analytical baseline vs direct surrogate,
- analytical baseline vs residual surrogate,
- direct surrogate vs residual surrogate.

## Success criteria

The project is considered successful if:
- Kwant spectra are generated reliably,
- the dataset passes sanity checks,
- at least one simple surrogate model predicts low-energy levels reasonably well,
- the surrogate is faster than direct Kwant computation,
- the results are clear enough for a diploma defense.

Practical target quality:
- excellent: about 1–2% relative test error,
- good: about 2–5% relative test error,
- acceptable for defense: about 5–8% if the methodology is clear, stable, and physically sensible.

## Notes

This is a minimal and defendable diploma project.
Simplicity, reproducibility, and scientific clarity are more important than sophistication.

The residual / delta-learning approach is not assumed to be automatically better.
It must be validated experimentally and only kept if it gives a clear advantage.
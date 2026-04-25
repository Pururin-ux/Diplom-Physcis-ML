# Diploma Physics ML

This project is a diploma prototype for building and evaluating surrogate modeling
workflows for low-energy spectra of 2D quantum dots computed with Kwant.

## Project goal

The near-term goal is to establish a reliable validation benchmark on a simple
rectangular quantum dot. The future main nontrivial target is a superellipse
geometry family, where shape variation is richer and scientifically more
informative for surrogate modeling.

## Scope

This project is intentionally narrow and minimal.

Current benchmark case:
- a simple closed 2D rectangular quantum dot,
- a square-lattice tight-binding model in Kwant,
- 2 input parameters: `Lx` and `Ly`,
- 4 output energy levels: `E0`, `E1`, `E2`, `E3`.

Future main nontrivial case:
- a superellipse geometry family (parameterized shape beyond a pure rectangle),
- same conservative low-energy focus before any model-complexity increase.

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

For the rectangular benchmark, ML is not the main scientific goal.
It is used as a conservative validation check of data/solver quality and
baseline workflow behavior.

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

This milestone is benchmark/validation only and should not be presented as
methodological novelty.

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
# Diploma Physics ML

This project is a diploma prototype for computing and conservatively evaluating
surrogate approximations for low-energy spectra of 2D quantum dots computed with
Kwant.

## Project goal

The rectangular quantum dot is used as a validation/control benchmark only.  The
current main research path is the fixed discrete-`n` superellipse quantum-dot
family, where shape variation is richer than in the rectangular control case.

The current completed result is Milestone 06c: consolidation of a
physics-informed Ridge baseline for the fixed discrete-`n` superellipse path.
MLP ablation studies and inverse design remain next/future work, not completed
claims.

## Scope

This project is intentionally narrow and minimal.

Validation/control benchmark:
- a simple closed 2D rectangular quantum dot,
- a square-lattice tight-binding model in Kwant,
- 2 input parameters: `Lx` and `Ly`,
- 4 output energy levels: `E0`, `E1`, `E2`, `E3`.

Current main nontrivial path:
- fixed discrete-`n` superellipse quantum dots,
- the same square-lattice tight-binding convention,
- the same conservative low-energy focus before any model-complexity increase.

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

The project has conservative model levels:

1. Analytical baseline  
2. Physics-informed Ridge baseline / checked direct surrogate approximations  
3. Optional residual or neural surrogate studies, only if validated honestly

For the rectangular benchmark, ML is not the main scientific goal. It is used as
a conservative validation check of data/solver quality and baseline workflow
behavior. For the superellipse path, ML models are treated as checked surrogate
approximations, not as sources of physical knowledge. All conclusions must be
checked against direct numerical calculations, control cases, reproducibility
checks, and honest validation protocols.

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
- closed 2D quantum dot, with the rectangle as the control case and fixed
  discrete-`n` superellipses as the current main path,
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

## Current milestone state

Completed benchmark/control work:
- simple rectangular quantum dot in Kwant,
- first 4 low-energy eigenenergies,
- physical sanity checks and basic parameter sweeps.

Current completed main-path result:
- Milestone 06c consolidates a physics-informed Ridge baseline for fixed
  discrete-`n` superellipse quantum dots.

Next/future work:
- MLP ablation as a prepared but not yet completed notebook milestone,
- inverse design as future work only.

The rectangular benchmark is validation/control only and should not be presented
as methodological novelty.

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
- analytical baseline vs physics-informed Ridge/direct surrogate,
- analytical baseline vs residual surrogate if implemented,
- direct surrogate vs residual surrogate if implemented.

## Success criteria

The project is considered successful if:
- Kwant spectra are generated reliably,
- the dataset passes sanity checks,
- a simple checked surrogate approximation predicts low-energy levels reasonably well,
- any surrogate is validated against direct Kwant computation and control cases,
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
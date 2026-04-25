# Project Instructions

## Goal
Build a minimal, defendable diploma project with two clear stages:
1) rectangular quantum dot as a validation/benchmark case,
2) superellipse-family quantum dots as the future main nontrivial target.
Use surrogate ML as a tool, not as an end in itself.

## Hard Constraints
- The project must stay realistic for one student in ~6 weeks.
- Prefer simplicity over ambition.
- Do NOT introduce full DOS, inverse design, PINNs, transformers,
  CNN/ResNet, HDF5, Dask, W&B/MLflow, or complex MLOps unless explicitly requested.
- Minimize dependencies and keep the code easy to debug.
- Use notebooks only for exploration and presentation, not for core logic.
- Do NOT expand scope without explicit user approval.

## Physics Scope
- Rectangular case: simple closed 2D rectangular quantum dot in Kwant
  used for validation and benchmarking.
- Future main case: superellipse geometry family in Kwant as the primary
  nontrivial target after the rectangular benchmark is stable.
- Lattice: square lattice, tight-binding model.
- Inputs: exactly 2 parameters — Lx (width) and Ly (height) in lattice units.
- Outputs: first 4 eigenenergies only: E0, E1, E2, E3.
- Preferred output encoding:
  E0, Δ1 = E1 - E0, Δ2 = E2 - E1, Δ3 = E3 - E2.
- Preferred Hamiltonian extraction:
  finalized system + hamiltonian_submatrix(sparse=True, params=...).
- Preferred eigensolver:
  scipy.sparse.linalg.eigsh for low-energy levels.
- Ensure the solver targets the lowest physically relevant eigenenergies,
  not the top of the spectrum.
- In the default setup, prefer `which='SA'`.
- Use shift-invert (`sigma=...`) only if there is a clear reason to target
  eigenvalues near a chosen reference energy, and explain that reason first.

## Baseline
- Use a particle-in-a-box-inspired analytical baseline in arbitrary/model units.
- Preferred scaling:
  E ~ (nx^2 / Lx^2 + ny^2 / Ly^2)
- If needed, calibrate the baseline scale to the Kwant convention.

## Model Strategy
- Treat the analytical baseline as the simplest reference model.
- For the rectangular benchmark, do not position ML as the main scientific goal;
  use it conservatively to validate pipeline consistency and error metrics.
- Treat the direct surrogate as the default minimal ML model once benchmark
  validation is complete.
- Treat the residual surrogate as an optional hypothesis, not as a guaranteed improvement.
- Do NOT assume delta-learning is novel by itself.
- Do NOT assume residual learning must outperform the direct model.
- Keep the residual model only if experiments show a clear benefit over:
  1. the analytical baseline,
  2. the direct surrogate.

## Physics Sanity Checks
- Energies must be finite real numbers.
- Energies must be sorted in nondecreasing order:
  E0 <= E1 <= E2 <= E3
- No NaN / Inf anywhere.
- Energies must change when Lx or Ly changes.
- When both Lx and Ly increase together, low energy levels should generally decrease.
- Re-running the same configuration must reproduce the same result.

## Dataset
- Default dataset: regular grid over Lx and Ly.
- Default grid size: 20 x 20 = 400 configurations.
- Default Lx range: [10, 30] lattice units.
- Default Ly range: [10, 30] lattice units.
- For debugging, smaller grids are allowed before running the full dataset.
- Storage: simple NumPy `.npz` format unless explicitly changed.
- After generation, run sanity checks on the full dataset.

## Models (in order of priority)
1. Analytical baseline
2. Direct MLP surrogate
3. Residual MLP surrogate

## ML Simplicity Rules
- Prefer the simplest working implementation first.
- Prefer scikit-learn for the first minimal surrogate unless PyTorch is explicitly needed.
- Do not introduce deep or complex architectures unless explicitly requested.
- Accuracy, reproducibility, and clarity are more important than sophistication.
- Use the direct surrogate as the main baseline ML experiment.
- Add the residual surrogate only after the direct model is working and evaluated.

## Evaluation Rules
- Always compare:
  - analytical baseline,
  - direct surrogate,
  - residual surrogate (if implemented).
- Use at least:
  - MAE or RMSE,
  - relative error in percent,
  - error relative to level spacing.
- If residual learning does not provide a clear improvement, say so explicitly.
- Never overclaim novelty or performance.
- Do not claim novelty for the rectangular benchmark case; it is a control/validation setup.

## Coding Rules
- Put all reusable logic in `src/`.
- Keep notebooks thin — they should call functions from `src/`.
- Add or update tests in `tests/` for important logic.
- Do not refactor unrelated files.
- Before editing: explain the plan in 2–3 sentences.
- After editing: report which files changed and what was tested.
- Use type hints and docstrings for all functions in `src/`.

## Communication Style
- Be concise and practical.
- If the task is too broad, narrow it first and explain the narrowed scope.
- If something is physically ambiguous, say so explicitly.
- Prefer one minimal working version first, then optional improvements.
- Never silently expand scope.
- Never describe the method as unique unless that is explicitly justified.
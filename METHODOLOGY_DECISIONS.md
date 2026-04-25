# Methodology Decisions

## Purpose

This document records methodology decisions before the next experiments. The goal is to avoid post-hoc interpretation and to keep the project scientifically checkable.

## Current stable state

- Rectangular quantum dot is used only as validation/control benchmark.
- Main path is fixed discrete-n superellipse quantum dots.
- Completed result is Milestone 06c: physics-informed Ridge baseline.
- ML models are treated as checked surrogate approximations, not sources of physical truth.
- Kwant forward calculation remains the source of truth.

## Physical literature positioning

- The physical model belongs to the class of discrete / tight-binding quantum billiards: finite domains on a square lattice with open hard-wall boundaries.
- Closest prior work includes:
  - Kwant workflows for tight-binding Hamiltonians and finite geometries.
  - Tight-binding / discrete quantum billiards on finite lattice domains.
  - Quantum billiards and symmetry/degeneracy literature for interpreting unstable level gaps.
- The project does not claim novelty in constructing lattice billiards.
- The contribution is a controlled surrogate-modeling workflow for fixed discrete-n superellipse tight-binding domains:
  - low-energy physical sanity checks;
  - physics-informed Ridge baseline;
  - structured LOAO/LOARO validation;
  - tiny MLP ablation with pre-registered criteria;
  - residual analysis against edge-discretization quantities;
  - optional Kwant-validated inverse screening.

## Energy convention

The kinetic energy used in continuum-like checks depends on the Hamiltonian convention:

- if onsite = 0 and hopping = -1, use E_kin = E0 + 4;
- if onsite = 4 and hopping = -1, use E_kin = E0.

The actual convention must be verified from src/geometry.py before plotting scaling diagnostics.

## Physical sanity checks before MLP

Scientific question:

"Does the fixed discrete-n superellipse dataset lie in a low-energy quadratic tight-binding regime where the 1/a^2 scaling is physically justified?"

- Check E_kin * a^2 vs a.
- As an additional support for the main gap target, dE1 * a^2 may also be inspected.
- Do not claim data efficiency.
- The minimum required dataset size is not investigated in this work.
- The physical regime justifying the 1/a^2 scaling is checked numerically; the physics-informed features are grounded in this regime.
- Do not claim the physics-informed features are globally optimal.

## Bessel / circle benchmark

- For n = 2.0 and aspect_ratio = 1.0, use an effective radius:
  R_eff = sqrt(N_sites / pi).
- Compare E_kin with:
  E_Bessel = j_01^2 / R_eff^2,
  where j_01 = 2.4048255577.
- This is an asymptotic continuum sanity check, not an exact equality on the square lattice.
- This benchmark is not a proof of the continuum limit. It is a check of the low-energy tight-binding scaling and the effective continuum scale in the selected design window.
- Pre-registered pass criterion:
  Bessel benchmark is considered acceptable if relative_error = abs(E_kin - E_Bessel) / E_Bessel < 10% at a = 36.
- If the error is larger, the cause must be analyzed before moving to ML conclusions.

## dE2 diagnostic-only decision

- dE2 is not used as a main MLP target.
- Before MLP, show the full table for:
  n = 2.0,
  aspect_ratio = 1.0,
  a in [24, 27, 30, 33, 36],
  columns: a, E0, E1, E2, E3, dE1, dE2, dE3.
- Purpose: demonstrate near-degeneracy/sensitivity instead of merely declaring dE2 difficult.

## Sublattice imbalance diagnostic

- For each geometry, compute:
  N_A = number of sites with (x + y) even,
  N_B = number of sites with (x + y) odd,
  delta_N = N_A - N_B,
  imbalance_ratio = abs(delta_N) / N_sites.
- This is a diagnostic inspired by tight-binding billiards and sublattice/chiral symmetry.
- Zero modes related to sublattice imbalance occur near E = 0 in the onsite=0 convention, i.e. near the middle of the [-4, 4] band, so they are not expected to directly control the lowest levels E0 and E1.
- The diagnostic is still useful to flag geometry-induced lattice effects.

## Fixed discrete-n decision

- n values are fixed classes: [1.2, 2.0, 3.0, 4.0].
- n is not treated as a smooth continuous input feature for the small models.
- n = 1.2 should be described as a rhombus-like convex shape with sharper boundary regions and stronger sensitivity to square-lattice discretization.
- Do not describe n = 1.2 as concave or as a topology change.

## MLP ablation decision

- MLP is a control experiment, not the main project line.
- MLP hidden_layer_sizes is fixed to (4,), not (16,).
- Reason: each n-class has only 35 samples, and LOAO/LOARO train folds have about 28-30 samples. A 4-neuron MLP keeps capacity comparable to the dataset size.
- Use no hyperparameter tuning.
- MLP must use feature scaling and target scaling.
- MLP targets: E0 and dE1 only.
- dE2 remains diagnostic-only.

## Pre-registered MLP success criterion

MLP+physics-informed is considered meaningfully better than Ridge+physics-informed only if:

1. It improves MAE by at least 15% relative to Ridge in at least 10 of the 16 main comparison cells:
   4 n-values x 2 targets x 2 validation protocols.

2. The improvement is present in both validation protocols:
   at least 5 of 8 LOAO cells and at least 5 of 8 LOARO cells must satisfy the 15% threshold.

3. Seed stability supports the improvement.

Justification:
The 15% threshold is chosen before looking at results as a conservative practical minimum. With only 35 samples per n-class, smaller gains are difficult to distinguish from fold variability, boundary-discretization effects, and small-sample variation.

Seed stability:
For 10 random_state values:

Delta_MAE = Ridge_MAE - mean(MLP_MAE)
SE = std(MLP_MAE) / sqrt(10)

The MLP improvement is considered unstable if:

Delta_MAE <= 2 * SE

If the criterion is not met, Ridge remains the preferred model because it is interpretable, stable, and physically grounded.

## Residual / edge-discretization hypothesis

"Systematic Ridge residuals are expected to correlate with edge-discretization quantities such as N_sites / analytic_area or N_sites - analytic_area. If confirmed, this supports the interpretation that Ridge captures the main continuum scaling while the residual reflects square-lattice boundary discretization."

## Known literature limitations

- Direct literature on edge-discretization effects for superellipse boundaries on square lattices is limited; this must be checked numerically in this work.
- Tiny MLP ablation in this exact setting is exploratory.
- The selected physics-informed features are physically motivated by low-energy scaling but are not claimed to be uniquely optimal.

## Inverse design decision

- Inverse design is future work after physical checks, MLP ablation, and residual analysis.
- Use grid search over the surrogate inside the training domain.
- No extrapolation outside a in [24, 36] and aspect_ratio in [0.67, 1.0].
- Every candidate found by the surrogate must be verified by direct Kwant calculation.
- The final physical result is the Kwant validation, not the surrogate prediction.

## External feedback / forums

- Do not ask broad forum questions before step 07.
- If physical sanity checks fail or are ambiguous, ask a narrow technical question in a relevant community.
- Do not ask forums to review the entire diploma methodology.

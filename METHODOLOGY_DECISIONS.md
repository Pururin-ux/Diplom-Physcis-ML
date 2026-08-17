# Methodology notes

This file summarizes the main modelling choices used in the diploma project.

## Physical model

The calculations use finite tight-binding domains on a square lattice. Direct Kwant calculations are the reference throughout the project. For the Hamiltonian with onsite energy 0 and hopping -1, the low-energy quantity used in continuum checks is `E_kin = E0 + 4`.

The main geometry family is a set of superellipses with fixed `n = 1.2, 2.0, 3.0, 4.0`. The rectangular dot is used only as a control calculation. The training range is limited to the geometries present in the dataset.

## Physical checks

Before comparing surrogate models, I checked whether the selected geometries remain in the expected low-energy regime. The main diagnostics are the `1/a^2` scaling and a circular-dot comparison using the first Bessel zero. The Bessel comparison is only a continuum sanity check for the lattice calculation, not an exact benchmark.

`dE2` is kept as a diagnostic quantity because level ordering and near-degeneracy make it less stable than `E0` and `dE1` for this dataset.

I also record sublattice imbalance and simple boundary-discretization quantities to see whether they explain systematic residuals.

## Surrogate models

The main surrogate is a physics-informed Ridge regression. A small MLP with one four-neuron hidden layer is used as a control comparison. Both are evaluated with structured holdout schemes rather than a random train/test split.

The MLP is not tuned extensively because each `n` class contains only 35 samples. The goal is to test whether a small nonlinear model gives a repeatable improvement, not to maximize neural-network capacity.

The surrogate is never used as a replacement for the direct calculation. Any future inverse search would remain inside the sampled parameter range and candidate geometries would need to be checked again with Kwant.

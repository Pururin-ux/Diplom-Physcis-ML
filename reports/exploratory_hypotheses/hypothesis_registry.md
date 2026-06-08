# Exploratory Hypothesis Registry

This registry is for exploratory hypothesis sprints after the closed Q/S
inverse-screening line. Entries are not preregistered results and must not be
used to revise the frozen S-objective outcome retroactively.

## Template

For each hypothesis:

- Hypothesis ID
- Physical idea
- Why it might be nontrivial
- Minimal computational test
- Strongest baseline
- Failure condition
- Expected runtime
- Status
- Verdict

## H1_boundary_defect

- Hypothesis ID: H1_boundary_defect
- Physical idea: Test whether local boundary defects or indentations can
  produce spectral or wavefunction changes not reducible to global
  aspect_ratio.
- Why it might be nontrivial: Local boundary perturbations can alter boundary
  scattering and mode structure without changing the global anisotropy
  descriptor strongly.
- Minimal computational test: Compare matched-Ekin geometries with and without
  a small local indentation or boundary defect under direct Kwant verification.
- Strongest baseline: Matched global aspect_ratio superellipse or simple
  anisotropy heuristic.
- Failure condition: Defect effects are explained by Ekin, N_sites, imbalance,
  or global aspect_ratio with no residual spectral or wavefunction signal.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

## H2_wavefunction_localization

- Hypothesis ID: H2_wavefunction_localization
- Physical idea: Test objectives based on wavefunction density localization
  near boundary/corners rather than energy gaps alone.
- Why it might be nontrivial: Spatial eigenstate structure may reveal boundary
  physics that scalar energy gaps collapse or obscure.
- Minimal computational test: Compute low-level eigenvectors for matched
  geometries and measure boundary/corner localization diagnostics.
- Strongest baseline: Simple geometry descriptors and anisotropy-controlled
  localization baseline.
- Failure condition: Localization metrics track only size, aspect_ratio, or
  rasterization artifacts.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

## H3_level_rearrangement

- Hypothesis ID: H3_level_rearrangement
- Physical idea: Search for avoided crossings or level-order changes under
  shape variation, instead of monotonic gap maximization.
- Why it might be nontrivial: Level rearrangements can indicate shape-driven
  spectral structure not captured by monotonic global descriptors.
- Minimal computational test: Sweep a small shape path with direct Kwant levels
  and track near-crossings or ordering changes among low eigenstates.
- Strongest baseline: Smooth monotonic interpolation in aspect_ratio and Ekin.
- Failure condition: Apparent rearrangements vanish under denser sampling,
  geometry deduplication, or rasterization robustness checks.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

## H4_residual_physics

- Hypothesis ID: H4_residual_physics
- Physical idea: Analyze residuals after simple physics/Ridge baseline to see
  whether any structured physical signal remains.
- Why it might be nontrivial: Residual structure could identify missing
  geometry descriptors or boundary terms beyond basic confinement scaling.
- Minimal computational test: Fit the existing simple physics/Ridge baseline,
  inspect residuals against geometry diagnostics, and verify any proposed
  residual feature on held-out groups.
- Strongest baseline: Existing physics-informed Ridge model.
- Failure condition: Residuals are noise-like, fold-specific, or explained by
  already known discretization diagnostics.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

## H5_lattice_artifact_robustness

- Hypothesis ID: H5_lattice_artifact_robustness
- Physical idea: Test whether spectral effects survive sub-lattice center
  shifts and rasterization changes.
- Why it might be nontrivial: Continuous shape parameters map to stepwise
  discrete Kwant domains, so some effects may be lattice artifacts rather than
  physical shape signals.
- Minimal computational test: Recompute selected geometries under controlled
  center shifts or rasterization variants and compare spectra and hashes.
- Strongest baseline: Same continuous parameters with alternate realized
  lattice domains.
- Failure condition: Claimed spectral effects change sign, disappear, or are
  dominated by rasterization choices.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

## H6_shape_family_comparison

- Hypothesis ID: H6_shape_family_comparison
- Physical idea: Compare superellipse, ellipse, stadium, rounded rectangle,
  perturbed circle, and indentation families under matched Ekin/N_sites
  constraints.
- Why it might be nontrivial: Different boundary families may produce
  non-monotonic spectral or wavefunction behavior absent in fixed-n
  superellipses.
- Minimal computational test: Build a small direct-Kwant matched-control grid
  across shape families, deduplicate realized geometries, and compare against
  physics baselines.
- Strongest baseline: Matched Ekin/N_sites plus aspect_ratio-controlled
  baseline within the same family.
- Failure condition: Cross-family effects reduce to Ekin, N_sites,
  aspect_ratio, or rasterization differences.
- Expected runtime: Not estimated.
- Status: NOT RUN
- Verdict: NOT RUN

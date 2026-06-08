# Pre-execution physics interpretation note

This note was written before the full S-objective execution. Its purpose is to
fix the intended interpretation and prevent post-hoc meaning-making.

## Known / Expected Physics

- Anisotropy of the confinement geometry is expected to split near-degenerate
  excited states.
- `Q = dE1 / Ekin` tends to increase toward isotropy and decrease with
  increasing anisotropy in the already computed diagnostics.
- A trade-off between increasing `S = (E2 - E1) / Ekin` and preserving Q is
  therefore expected.

## Nontrivial Question

The nontrivial question is not whether anisotropy splits levels. The question is
whether surrogate-guided inverse screening can find candidates that beat strong
baselines under fixed-Ekin and Q-preservation constraints.

The experiment is a benchmark of ML/surrogate usefulness under the frozen
protocol, not a claim that anisotropy-induced splitting is newly discovered.

## What Is Not Claimed

- No discovery of anisotropy-induced excited-state splitting is claimed.
- No topological novelty is claimed.
- No inverse-design or inverse-screening success is claimed unless the frozen
  success criteria are met.
- Surrogate-only values are not physical evidence for final claims.

## Decision Rules

- Primary success: all 4 `n` values pass at `alpha = 0.95`.
- Partial support: exactly 3/4 `n` values pass at `alpha = 0.95`.
- Exploratory / shape-dependent: 1-2/4 `n` values pass at `alpha = 0.95`.
- Negative result: 0/4 `n` values pass at `alpha = 0.95`.
- `alpha = 0.90` is secondary and cannot override primary failure.
- Beating isotropic same-`n` alone is insufficient.
- Failure to beat the simple anisotropy heuristic means the result is a
  monotonic anisotropy diagnostic, not inverse-screening success.

## Metadata

- `preregistration_commit = 7e28542fda40db288ad2613b49f17b1248f6f2ce`
- `implementation_commit = 6b256287820ed29811460051855700e9b923a92f`
- `rules_changed_after_execution = False`
- `note_written_before_full_execution = True`

# S-objective execution report

This report is the preregistered S-objective execution under the frozen
protocol. It tests whether surrogate-guided screening adds nontrivial
value beyond strong physics-based baselines. It does not claim discovery
of anisotropy-induced splitting.

## Frozen decision rules

- Primary alpha: `0.95`.
- Secondary alpha: `0.90`; secondary results cannot override primary failure.
- Primary success: all 4 fixed `n` values pass at alpha `0.95`.
- Partial support: exactly 3/4 fixed `n` values pass at alpha `0.95`.
- Exploratory / shape-dependent: 1-2/4 fixed `n` values pass at alpha `0.95`.
- Negative result: 0/4 fixed `n` values pass at alpha `0.95`.
- Beating isotropic same-`n` alone is insufficient.
- Failure to beat the simple anisotropy heuristic means S behaves as a monotonic anisotropy diagnostic, not inverse-screening success.

## Outputs

- `s_candidates_verified.csv`: direct-Kwant method candidates.
- `baselines_by_n.csv`: direct-Kwant or already Kwant-computed baselines.
- `random_baseline_repeats.csv`: deterministic random best-of-5 repeats.
- `summary_by_n.csv`: frozen pass/fail classifications.
- `execution_audit.md`: execution provenance and warnings.

Plots were not generated in this execution. This avoids delaying the
frozen-rule run for presentation work; the CSV outputs are the primary
record.

## Conclusions

- Primary alpha result: negative result (0/4 passed).
- Secondary alpha result: negative result (0/4 passed under alpha=0.90 evaluation).

## Per-n summary

- n=1.2: pass=False; strongest=simple_anisotropy_heuristic; beat_simple=False; physical doublet-splitting effect observed, but no inverse-screening advantage. | S behaves as a monotonic anisotropy diagnostic rather than a non-trivial inverse-screening objective in this tested domain.
- n=2.0: pass=False; strongest=simple_anisotropy_heuristic; beat_simple=False; physical doublet-splitting effect observed, but no inverse-screening advantage. | S behaves as a monotonic anisotropy diagnostic rather than a non-trivial inverse-screening objective in this tested domain.
- n=3.0: pass=False; strongest=simple_anisotropy_heuristic; beat_simple=False; physical doublet-splitting effect observed, but no inverse-screening advantage. | S behaves as a monotonic anisotropy diagnostic rather than a non-trivial inverse-screening objective in this tested domain.
- n=4.0: pass=False; strongest=simple_anisotropy_heuristic; beat_simple=False; physical doublet-splitting effect observed, but no inverse-screening advantage. | S behaves as a monotonic anisotropy diagnostic rather than a non-trivial inverse-screening objective in this tested domain.

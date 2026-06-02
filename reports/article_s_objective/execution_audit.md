# S-objective execution audit

## Provenance

- execution_branch: `article-s-objective-execution`
- preregistration_commit: `7e28542fda40db288ad2613b49f17b1248f6f2ce`
- implementation_commit: `6b256287820ed29811460051855700e9b923a92f`
- pre_execution_note_commit: `4fbb954`
- execution_commit: `60517c8a4e880ef30cee59dd3774cd0c246d6f44`
- post_execution_audit_update: provenance-only; no final CSV/result values modified
- conda_environment: `diplom-kwant`

## Commands Run

Pre-execution tests:

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests\test_s_objective_screening.py -q
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q
```

Results:

- targeted S-objective tests: `24 passed`
- full test suite: `82 passed`, with one known OpenMP warning

Full execution:

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python scripts\run_s_objective_screening.py --run-final
```

Runtime:

- runner-reported runtime: `145.149 s`
- PowerShell wall-clock runtime: `147.773 s`

Final post-execution tests:

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests\test_s_objective_screening.py -q
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q
```

Results:

- targeted S-objective tests: `24 passed in 1.26s`
- full test suite: `82 passed in 2.75s`, with one known OpenMP warning

## Files Produced

Final S-objective outputs:

- `reports/article_s_objective/s_candidates_verified.csv`
- `reports/article_s_objective/baselines_by_n.csv`
- `reports/article_s_objective/random_baseline_repeats.csv`
- `reports/article_s_objective/summary_by_n.csv`
- `reports/article_s_objective/README.md`

Audit/provenance files:

- `reports/article_s_objective/pre_execution_physics_note.md`
- `reports/article_s_objective/execution_audit.md`

Plots:

- no plots were generated
- README states that plots were not generated

## Output Counts

- method candidate rows: `34`
- baseline rows: `32`
- random repeat rows: `2000`
- summary rows: `8`

## Rule Status

- frozen rules changed: no
- primary alpha changed: no, remains `0.95`
- secondary alpha changed: no, remains `0.90`
- `delta_S_min` changed: no
- top-k changed: no
- random baseline rules changed: no
- Ekin tolerance changed: no
- thesis files modified: no
- full experiment was run: yes
- final CSV/README outputs edited manually after execution: no
- `execution_audit.md` was written manually after execution as an audit record

## Warnings and Exceptions

- Full execution raised no exceptions.
- Full execution did not print the OpenMP warning.
- Test runs emitted the known existing `threadpoolctl` warning about Intel
  OpenMP and LLVM OpenMP both being loaded. This warning appeared in earlier
  non-S-objective test runs and is not specific to the S-objective execution.

## Result Classification

Frozen primary-alpha result:

- `alpha = 0.95`
- passed `n` values: `0/4`
- classification: negative result

Frozen secondary-alpha result:

- `alpha = 0.90`
- passed `n` values: `0/4`
- classification: negative result
- secondary alpha cannot override primary failure

For every `n` and alpha, the strongest feasible baseline was the simple
anisotropy heuristic. The method did not beat that heuristic by `delta_S_min`.
Therefore the result is not inverse-screening success under the frozen protocol.

The appropriate interpretation is:

> S behaves as a monotonic anisotropy diagnostic rather than demonstrating
> nontrivial inverse-screening advantage.

## Closure Note

The Q/S inverse-screening line is closed as a negative result under the frozen
protocol. Q is symmetry-biased toward isotropy. S behaves as a monotonic
anisotropy diagnostic in the tested superellipse domain. Surrogate-guided
one-shot screening did not outperform strong physics baselines.

Do not perform S-objective rescue runs without a new explicitly exploratory
protocol.

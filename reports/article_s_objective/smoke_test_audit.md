# S-objective Kwant smoke verification audit

This file is an implementation smoke-test audit log only. It is not a
scientific S-objective result, not a final experiment report, and not an
article draft.

## Commits

- implementation_commit: `eed47b044ce1a0eeb4885dfa3aa42a25efad3d09`
- preregistration_commit: `7e28542fda40db288ad2613b49f17b1248f6f2ce`
- branch: `article-s-objective-implementation`

## Commands Run

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests\test_s_objective_screening.py -q
```

Result: `17 passed in 1.53s`.

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python -m pytest tests -q
```

Result: `75 passed in 3.36s`, with one known OpenMP runtime warning from
`threadpoolctl` during `tests/test_model_baselines.py::test_run_baseline_stress_test_protocol_keys`.

```powershell
C:\Users\lalad\miniforge3\Scripts\conda.exe run -n diplom-kwant python scripts\run_s_objective_screening.py --max-kwant-per-n 2
```

Wall-clock runtime: approximately `19.672 s`.

Printed smoke output:

```text
Frozen preregistration commit: 7e28542fda40db288ad2613b49f17b1248f6f2ce
Ekin targets: {1.2: 0.010689289799576063, 2.0: 0.007727409624868287, 3.0: 0.007053480364534792, 4.0: 0.006858160651241896}
Future output schemas: s_candidates_verified.csv, baselines_by_n.csv, random_baseline_repeats.csv, summary_by_n.csv
Final S-output writing is disabled in this implementation commit.
n=1.2: smoke_kwant=2, finite_S=2
n=2.0: smoke_kwant=2, finite_S=2
n=3.0: smoke_kwant=2, finite_S=2
n=4.0: smoke_kwant=2, finite_S=2
EXIT_CODE=0
RUNTIME_SECONDS=19.672
```

## Smoke-Test Result

Direct Kwant integration passed the capped smoke verification:

- `n = 1.2`: `2/2` capped rows had finite S.
- `n = 2.0`: `2/2` capped rows had finite S.
- `n = 3.0`: `2/2` capped rows had finite S.
- `n = 4.0`: `2/2` capped rows had finite S.

No exceptions were raised during the capped smoke verification. The capped
smoke command did not print the OpenMP warning.

## Optional Feasibility Probe

A local no-output diagnostic was run for `n = 2.0` only. This was not the full
experiment and did not write final outputs.

Result:

```text
n=2.0
top5_method_candidates=5
ekin_feasible_alpha095_context=5
q_feasible_alpha095=0
both_ekin_and_q_feasible_alpha095=0
q_iso=1.5367475903700423
```

This probe only checks implementation plumbing and preliminary feasibility for
one fixed `n`. It must not be treated as a scientific result.

## Output Policy Check

- Full S-objective experiment was run: no.
- Final S outputs were produced: no.
- Final candidate CSV was produced: no.
- Final baseline CSV was produced: no.
- Random-baseline repeats CSV was produced: no.
- `summary_by_n.csv` was produced: no.
- S plots were produced: no.
- S README was produced: no.
- Thesis files were modified: no.
- Frozen preregistration rules were modified: no.

## Known Warnings

The full test suite emitted the known existing `threadpoolctl` warning about
Intel OpenMP and LLVM OpenMP both being loaded. This warning also appeared in
the previous implementation test run and is not specific to the S-objective
smoke command.

## Remaining Blockers Before Full Execution

- Human/code review of the implementation branch.
- Explicit authorization to run the full S-objective experiment.
- Confirmation that final result-writing behavior should be enabled only after
  the frozen protocol and implementation are accepted.
- No protocol rule should be changed after the frozen preregistration commit
  without a new dated amendment commit.

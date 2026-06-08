# Bessel Anchor Convergence Review

## Review Scope

This is a review-only note for the existing Article Path B
`BESSEL_ANCHOR_ONLY` outputs. It reads the committed Bessel anchor spectra,
fit table, and summary. It does not run new spectra, does not compare
`n=1.2` or `n=4.0`, does not implement a finite-difference Laplacian, does not
use ML, and does not use Q or S objectives.

Important article relevance statement:

This review does not validate Path B. It only validates or questions the
circular Bessel anchor. No n-dependent residual claim is allowed from this
sprint.

## 1. Ground-State Convergence

Ground-state target: `level_0`, corresponding to continuum group `m0_s1`.

| diagnostic | value |
|---|---:|
| exponent alpha | 2.9610312165658064 |
| R2 | 0.9968518146230158 |
| RMSE | 1.0438496781498138e-05 |
| leave-one-size-out alpha min | 2.903763258731241 |
| leave-one-size-out alpha max | 3.0393974383576627 |
| leave-one-size-out stable | True |
| stability verdict | passed |

The ground-state residual magnitude decreases from
`2.1514615625528935e-04` at `a=24` to `4.02007982901902e-06` at `a=96`,
with ratio `0.0186853434845885`. The `a=96` point supports the decreasing
trend rather than breaking it.

## 2. Excited Levels / Degeneracy Groups

Individual-level absolute power-law fits:

| level | alpha | R2 | leave-one-size-out alpha range | stable |
|---|---:|---:|---|---|
| level_1 | 2.9831164670390957 | 0.9970789995261962 | 2.927608745326455..3.0563973717497137 | True |
| level_2 | 2.983116477191699 | 0.9970789996125461 | 2.9276087560401804..3.056397384861069 | True |
| level_3 | 3.0453474840573094 | 0.9947810105220429 | 2.9607869579207198..3.1564815179401338 | True |
| level_4 | 2.969291098696197 | 0.9988776824007284 | 2.934360526655022..3.010949873067801 | True |
| level_5 | 3.019856418762495 | 0.9973993814948005 | 2.9669813906093148..3.0853055542718164 | True |

Degeneracy-group absolute power-law fits:

| group | alpha | R2 | leave-one-size-out alpha range | stable |
|---|---:|---:|---|---|
| group_m0_s1 | 2.9610312165658064 | 0.9968518146230158 | 2.903763258731241..3.0393974383576627 | True |
| group_m0_s2 | 3.019856418762495 | 0.9973993814948005 | 2.9669813906093148..3.0853055542718164 | True |
| group_m1_s1 | 2.983116472115396 | 0.9970789995693712 | 2.9276087506833153..3.0563973783053897 | True |
| group_m2_s1 | 3.0102703200002296 | 0.9973566257009455 | 2.957283746345834..3.077116281205137 | True |

Degeneracy handling is clean enough for the anchor:

- `m1_s1` splitting is numerical-scale only, with maximum split
  `2.0161650127192843e-13`.
- `m2_s1` has visible square-lattice degeneracy lifting, with maximum split
  `0.00018957319238444015`, but the split decreases to
  `2.6214318626927e-07` at `a=96`.
- Both individual residuals and group-averaged residuals are reported, so the
  lifted degeneracy is not forced into a false one-to-one continuum
  interpretation.

## 3. Residual Behavior

Residual magnitude decreases with `a` for every reported level:

| level | \|R(a=96)\| / \|R(a=24)\| |
|---|---:|
| level_0 | 0.0186853434845885 |
| level_1 | 0.0180588623301347 |
| level_2 | 0.0180588619776801 |
| level_3 | 0.0172373317764872 |
| level_4 | 0.0173844096016218 |
| level_5 | 0.0170713985482669 |

The `a=96` point supports the convergence trend. It does not introduce a
late-size reversal or collapse of the fitted exponent.

The signed residual is not pathological in this anchor. All individual
level residuals are negative at both `a=24` and `a=96`, and the signed
power-law fits match the absolute fits with negative coefficients. There is no
sign flip that would make the signed residual model uninterpretable.

A single-power-law model is credible for the circular anchor review because:

- all absolute-fit R2 values are at least `0.9947810105220429`;
- all leave-one-size-out exponent ranges are narrow enough to be marked stable;
- fitted exponents cluster around alpha approximately `3`;
- residual magnitudes decrease consistently when `a=96` is included.

This credibility is limited to the circular Bessel anchor. It does not imply
that an n-dependent superellipse residual exists.

## 4. Final Review Verdict

ANCHOR_REVIEW_CONFIRMS_PASS

## 5. Recommendation

Proceed to FD-Laplacian implementation for minimal shape contrast test.

This recommendation means the anchor is reliable enough to justify the next
protocol-gated reference implementation step. It does not authorize a positive
Path B article claim, a full shape-comparison expansion, or any ML/surrogate
work.

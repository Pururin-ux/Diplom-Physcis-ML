# Article-F robustness checks R1-R4

Frozen definitions: protocol_addendum_1.md (commit 04e24a1).

## R1. Extrapolation-form robustness
- n=1.2: linear=6.0428 quad=6.0342 LOO range=[6.0407, 6.0462] full spread=0.0120 (0.20% of MFS) lin max resid=0.0014
- n=2.0: linear=5.7796 quad=5.7889 LOO range=[5.7785, 5.7829] full spread=0.0103 (0.18% of MFS) lin max resid=0.0015
- n=3.0: linear=5.8725 quad=5.8678 LOO range=[5.8692, 5.8786] full spread=0.0108 (0.18% of MFS) lin max resid=0.0035
- n=4.0: linear=5.9725 quad=5.9522 LOO range=[5.9682, 5.9838] full spread=0.0315 (0.53% of MFS) lin max resid=0.0050

## R2. MFS parameter robustness (n = 3.0, 4.0)
- n=3.0 lambda1: mean=5.21632360 spread=2.20e-05 (rel 4.2e-06)
- n=3.0 lambda2: mean=13.19018546 spread=3.23e-05 (rel 2.4e-06)
- n=4.0 lambda1: mean=5.05700916 spread=2.00e-04 (rel 3.9e-05)
- n=4.0 lambda2: mean=12.73060544 spread=6.84e-03 (rel 5.4e-04)

## R3. Orientation-effect decay with size
- n=1.2: Delta_theta = 0.0468 (a_circ=24), 0.0407 (a_circ=30), 0.0289 (a_circ=48); effective power p=0.70 (3-point estimate)
- n=4.0: Delta_theta = 0.0780 (a_circ=24), 0.0443 (a_circ=30), 0.0294 (a_circ=48); effective power p=1.33 (3-point estimate)

## R4. Sawtooth mechanism: perturbative weight of removed sites
- corr(dE1, w1) = +0.973
- corr(dE2, w2) = +0.999
- corr(dSplit, w2 - w1) = +1.000
- baseline corr(|dSplit|, removed count) = +0.983
- frozen rule outcome: weighted mechanism SUPPORTED (weighted correlation vs raw-count baseline)

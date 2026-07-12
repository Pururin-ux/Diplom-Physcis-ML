# Article-F checks R5-R6

Frozen definitions: protocol_addendum_2.md (commit f270595).

## R5. Low-rank Delta-H prediction in the doublet subspace
- dE0: median rel err 197.4%, max 419.8%
- dE1: median rel err 194.1%, max 326.5%
- dE2: median rel err 200.3%, max 424.8%
- dSplit: median rel err 212.4%, max 446.7%
- Pearson corr(dSplit_pred, dSplit_act) = +0.9997
- frozen rule outcome: qualitative agreement only (median dSplit rel err >= 25%)

## R6. Placement-averaged xi response
| xi | y centered | ensemble mean | ensemble std |
|---|---|---|---|
| 0.25 | 0.613 | 3.402 | 2.226 |
| 0.50 | 0.364 | 2.904 | 1.538 |
| 0.75 | 0.646 | 2.914 | 0.963 |
| 1.00 | 2.975 | 2.935 | 0.768 |
| 1.25 | 2.433 | 2.944 | 0.579 |
| 1.50 | 2.121 | 2.955 | 0.512 |
| 1.75 | 1.994 | 2.968 | 0.412 |
| 2.00 | 3.042 | 2.977 | 0.385 |
| 2.25 | 2.721 | 2.984 | 0.321 |
| 2.50 | 2.488 | 2.997 | 0.314 |
| 2.75 | 2.338 | 3.005 | 0.273 |
| 3.00 | 3.069 | 3.017 | 0.265 |
| 3.25 | 2.862 | 3.028 | 0.235 |
| 3.50 | 2.696 | 3.040 | 0.229 |
| 3.75 | 2.564 | 3.048 | 0.199 |
| 4.00 | 3.110 | 3.060 | 0.202 |

- TV(centered realization) = 7.38
- TV(ensemble mean) = 0.65
- fraction of placements with y < 1 at xi=0.25: 0.38
- fraction of placements with y < 1 at xi=0.5: 0.19
- fraction of placements with y < 1 at xi=0.75: 0.06

# Article-F checks R7-R8

Frozen definitions: protocol_addendum_3.md (commit d777647).

## R8. Exact Feshbach/T-matrix closure
- xi 0.75->1.0 E1: direct=-3.988277145421, exact-closure=-3.988277145421, |err|=2.71e-14
- xi 0.75->1.0 E2: direct=-3.987848997345, exact-closure=-3.987848997345, |err|=2.66e-15
- xi 1.0->1.25 E1: direct=-3.988262958481, exact-closure=-3.988262958481, |err|=8.88e-16
- xi 1.0->1.25 E2: direct=-3.987824696443, exact-closure=-3.987824696443, |err|=1.55e-14
- frozen PASS criterion (|err| < 1e-9 for all levels): PASS

Truncation study (relative error on the E+4 scale):
| step | level | m=4 | m=20 | m=100 | m=500 |
|---|---|---|---|---|---|
| xi 0.75->1.0 | E1 | 2.43e-03 | 2.01e-03 | 1.41e-03 | 2.93e-03 |
| xi 0.75->1.0 | E2 | nan | 3.89e-01 | 3.70e-01 | nan |
| xi 1.0->1.25 | E1 | 1.32e-02 | nan | nan | 5.77e-03 |
| xi 1.0->1.25 | E2 | 4.73e-01 | nan | nan | 1.56e-02 |

## R7. 8x8 placement ensemble, sizes 24/33/48
| a | xi | mean y (8x8) | std | frac y<1 |
|---|---|---|---|---|
| 24 | 0.25 | 3.284 | 2.167 | 0.25 |
| 24 | 0.50 | 2.894 | 1.188 | 0.11 |
| 24 | 0.75 | 2.901 | 0.924 | 0.05 |
| 24 | 1.50 | 2.949 | 0.405 | 0.00 |
| 24 | 3.00 | 3.030 | 0.211 | 0.00 |
| 33 | 0.25 | 3.271 | 2.121 | 0.25 |
| 33 | 0.50 | 2.908 | 1.147 | 0.11 |
| 33 | 0.75 | 2.913 | 0.883 | 0.05 |
| 33 | 1.50 | 2.945 | 0.385 | 0.00 |
| 33 | 3.00 | 3.009 | 0.198 | 0.00 |
| 48 | 0.25 | 3.260 | 1.978 | 0.20 |
| 48 | 0.50 | 2.917 | 1.091 | 0.11 |
| 48 | 0.75 | 2.923 | 0.830 | 0.05 |
| 48 | 1.50 | 2.943 | 0.369 | 0.00 |
| 48 | 3.00 | 2.988 | 0.189 | 0.00 |

4x4 (R6) vs 8x8 means at a = 33 (shared xi):
- xi=0.25: 4x4 mean=3.402, 8x8 mean=3.271
- xi=0.5: 4x4 mean=2.904, 8x8 mean=2.908
- xi=0.75: 4x4 mean=2.914, 8x8 mean=2.913
- xi=1.5: 4x4 mean=2.955, 8x8 mean=2.945
- xi=3.0: 4x4 mean=3.017, 8x8 mean=3.009

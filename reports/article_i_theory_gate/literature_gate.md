# Article-I literature and textbook gate

Purpose: before any further computation, establish which Article-F/G/H
observations are standard known physics/mathematics, what the current Article-H
observable actually measures, and whether a genuinely new question remains.
Primary sources only (monographs, original and review papers, math references);
no blogs or abstract-only claims.

Status legend: KNOWN TEXTBOOK RESULT | KNOWN LITERATURE RESULT |
KNOWN RESULT, NEW APPLICATION | POTENTIALLY NOVEL | NOVELTY NOT ESTABLISHED.

## Mapping table

| Our observation | Known result | Source | What matches | What might be new | Status |
|---|---|---|---|---|---|
| Fixed-`a` "shape effect" is mostly area; at fixed area the disk minimizes `lambda_1` | Faber-Krahn inequality; dimensional analysis | Faber 1923; Krahn, Math. Ann. 94 (1925); Brasco-De Philippis-Velichkov, Duke Math. J. 164 (2015) | disk is the fixed-area minimizer; residual O(few %) | nothing | KNOWN TEXTBOOK RESULT |
| First-excited disk doublet splits under the elliptical (area-preserving quadrupole) deformation with coefficient `chih_split = j11^2/j01^2 = 2.5387` | Hadamard shape derivative of a degenerate Dirichlet eigenvalue + classical circular-membrane / small-eccentricity-ellipse splitting | Sokolowski-Zolesio, *Introduction to Shape Optimization* (Springer 1992); Grinfeld, JOTA 145 (2010) "Hadamard's Formula Inside and Out"; Suzuki-Tsuchiya, J. Math. Soc. Japan 76 (2024), arXiv:2309.00273; Rayleigh, *Theory of Sound*; ellipse fundamental eigenvalue arXiv:1802.07768 | our own derivation + MFS reproduce 2.5387 exactly | nothing (this is the benchmark) | KNOWN TEXTBOOK RESULT |
| Ground eigenvalue is first-order invariant under the area-preserving quadrupole (moving denominator harmless at 1st order) | m=0 Hadamard integral of `cos 2phi` vanishes; Faber-Krahn stationarity at the disk | as above (Hadamard); Faber-Krahn | dlambda_0/ddelta = 0 at the disk confirmed by MFS | nothing | KNOWN TEXTBOOK RESULT |
| A degenerate doublet splits into analytic eigenvalue branches under deformation; tracked branches can exchange (swap) | Rellich-Kato analytic perturbation theory; avoided/true crossings | Rellich (1937-42); Kato, *Perturbation Theory for Linear Operators* (Springer 1966/1995); Simon, arXiv:1711.00528 | swap = branch reordering of a parametric eigenproblem | nothing | KNOWN TEXTBOOK RESULT |
| Sub-pixel placement lifts the `C4v` degeneracy already at `delta=0` (placement-induced baseline splitting) | symmetry lowering of an `E` doublet; spectral convergence of pixelated/rough domains to the Dirichlet Laplacian | Tinkham, *Group Theory and QM*; Rosler-Stepanenko, Math. Comp. 93 (2024), arXiv:2104.09444 (Mosco/norm-resolvent); Bramble-Hubbard, SIAM J. Numer. Anal. 5 (1968); Cicalese et al., arXiv:2504.21629 (discrete Faber-Krahn) | placement anisotropy = discretization/symmetry-lowering effect | nothing physical; a clean digital-domain fact | KNOWN LITERATURE RESULT |
| Article-H signed splitting: sorting the gap (`|E2-E1|`) creates a false positive; subtracting the placement baseline removes it | order statistics / absolute-value folding; baseline subtraction | elementary; same logic as reproducibility "baseline" critiques (methodological) | our exact `L_old = B_baseline + C_sorted_bc` decomposition | nothing physical; a correct methodological negative result | KNOWN RESULT, NEW APPLICATION |
| Lattice reproduces the continuum doublet split: symmetric-placement invariant response ~2.16 (n=2) approaches benchmark 2.54 | discrete-to-continuum spectral convergence of the lattice Laplacian; effective-mass band bottom `E+4 ~ k^2` | Nakamura-Tadano, arXiv:2006.00854 (continuum limit of lattice Schrodinger); standard tight-binding | our micro-pilot invariant split (symmetric placements) ~ benchmark | nothing (confirms known convergence) | KNOWN LITERATURE RESULT |
| Tight-binding billiard = smooth domain sampled on a square lattice; boundary becomes a high-order polygon | tight-binding / discrete billiards with curved hard walls | Ulcakar-Vidmar, Phys. Rev. E 106, 034118 (2022), arXiv:2206.07078; Cuevas-Louis-Verges, PRL 77, 1970 (1996); Fernandez-Hurtado et al., NJP 16, 035005 (2014) | identical model class | nothing in the model itself | KNOWN LITERATURE RESULT |
| n=4 (flat axis-aligned segments) shows heavier-tailed, shape-dependent digital response distribution than n=2 | lattice-point discrepancy for convex bodies with flat points and rational-normal directions; translation-variable L^p norms | Brandolini-Colzani-Gariboldi-Gigante-Travaglini, Rev. Mat. Iberoam. 36 (2020), arXiv:1807.07059; Gariboldi, Mathematika 66 (2020), arXiv:1904.02952; Iosevich-Sawyer-Seeger, J. Anal. Math. 101 (2007) | flat + rational-normal segments produce coherent, translation-dependent counting anomalies | applying discrepancy asymptotics to the *spectral* doublet response (eigenfunction-weighted, not bare counting) | KNOWN RESULT, NEW APPLICATION / NOVELTY NOT ESTABLISHED |
| Fixed-`xi = a*delta` double-scaling ensemble of the class-conditioned dimensionless doublet response, with its full non-Gaussian distribution and heavy tails | closest: lattice-point discrepancy over translations; but the eigenfunction-marked, doublet-response version is not found in the searched literature | (no direct source found) | the double-scaling regime `delta ~ 1/a` with signed/invariant doublet response as a marked digital-boundary statistic | POTENTIALLY NOVEL, pending a direct comparison to discrepancy theory and a mechanism analysis | NOVELTY NOT ESTABLISHED |

## Reading of the table

- Everything about the CONTINUUM shape response of the first-excited doublet
  (its sign, magnitude 2.5387, ground-state stationarity, branch splitting) is
  KNOWN TEXTBOOK physics. The lattice merely reproduces it (known convergence).
- The placement-induced baseline splitting and the sorted-gap false positive
  are correct but known/methodological.
- The ONLY candidate for genuine novelty is the fixed-`xi` double-scaling
  DIGITAL statistics of the doublet response (distribution, tails, symmetry-
  class conditioning) as a mesoscopic-spectral-statistics object. Even there,
  the natural theoretical home (lattice-point discrepancy with flat points and
  rational normals) is already highly developed, so novelty is NOT ESTABLISHED
  until our object is compared directly to that theory and a mechanism (coherent
  boundary events) is demonstrated, not merely asserted.

Consequently the central Article-H "negative signed response" is NOT a new
physical effect: as shown in `observable_invariance.md` and the micro-pilot,
the basis-invariant doublet response is positive and O(1) (continuum-like), and
the negative sign is a label-orientation artifact.

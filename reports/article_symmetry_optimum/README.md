# Symmetry optimum analysis

This report tests a physical explanation for the negative one-shot
surrogate-guided inverse-screening result. The question is whether, along
a surrogate iso-Ekin line, Q = dE1 / Ekin increases toward the isotropic
same-n geometry and whether anisotropy splits the first excited doublet.

This is a numerical test in the discrete square-lattice tight-binding
superellipse model. Continuum PPW/Ashbaugh-Benguria intuition is only an
analogy here, not proof for the lattice problem.

No new inverse-design objective is implemented in this analysis.

## Summary

- n=1.2: supports_symmetry_optimum=True; Q_iso_minus_best_noniso=0.05556638320800489; supports: splitting decreases toward isotropy
- n=2.0: supports_symmetry_optimum=True; Q_iso_minus_best_noniso=0.06520083987527969; supports: splitting decreases toward isotropy
- n=3.0: supports_symmetry_optimum=True; Q_iso_minus_best_noniso=0.06449724046914196; supports: splitting decreases toward isotropy
- n=4.0: supports_symmetry_optimum=True; Q_iso_minus_best_noniso=0.05855128822289912; supports: splitting decreases toward isotropy

The previous top inverse-screening candidate and the isotropic same-n
baseline are the same discrete geometry for every tested n.

## Implication for S = (E2 - E1) / Ekin

The normalized doublet splitting S is diagnostic only in this report. If
future work uses S as an objective, it must be pre-registered as a new
question and directly Kwant-verified against strong baselines. The
current analysis does not establish inverse-design success.

## Limitations

- Only representative points on the iso-Ekin line are Kwant-verified.
- Surrogate roots define the iso-Ekin line; final spectral values are
  direct Kwant values only at selected points.
- Continuous parameters can map to identical discrete lattice domains.
- Thesis chapters and thesis conclusions are not modified by this report.

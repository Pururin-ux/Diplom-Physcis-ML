# Article-Ic discrepancy gate: Model 0 vs Model 1

Leave-one-placement-out R^2 (ridge LS). Model 0 = bare geometry;
Model 1 = geometry + eigenfunction-weighted marks.

| target | shape | Model0 R2 | Model1 R2 | improvement | n |
|---|---|---|---|---|---|
| eta_gap | all | 0.414 | 0.907 | +0.493 | 1262 |
| abs_eta_gap | all | 0.507 | 0.847 | +0.340 | 1262 |
| eta_center | all | 0.856 | 0.921 | +0.066 | 1262 |
| eta_gap | 2.0 | 0.564 | 0.912 | +0.348 | 538 |
| abs_eta_gap | 2.0 | 0.591 | 0.914 | +0.322 | 538 |
| eta_center | 2.0 | 0.861 | 0.923 | +0.062 | 538 |
| eta_gap | 4.0 | 0.381 | 0.931 | +0.550 | 724 |
| abs_eta_gap | 4.0 | 0.555 | 0.854 | +0.298 | 724 |
| eta_center | 4.0 | 0.818 | 0.890 | +0.072 | 724 |

## Gate reading (automatic, naive)
- Model 1 improvement on |eta_gap| (all shapes, LOPLO): +0.340.

## Corrected interpretation (this is KNOWN physics, not a novelty candidate)

The automatic rule only checks "Model 1 beats Model 0". That check is passed
(eigenfunction weighting raises the gap-mark R^2 from 0.41 to 0.91, robustly
across shapes and placements). But this is EXACTLY the known finite-rank
result, not new structure:

- Model 0 (bare geometric counting) being insufficient for the GAP shift is the
  textbook statement that a finite-rank eigenvalue shift is a MATRIX ELEMENT,
  not a site count.
- Model 1's winning features (`boundary_weight_mode_j`, `changed_bond_weight`,
  `schur_predictor = w2 - w1`) ARE the Schur self-energy / boundary-deformation
  matrix element from `finite_rank_event_theory.md` and the literature gate
  (Krein spectral shift, Schur secular equation, Barnett-Cohen-Heller boundary
  matrix element). They are not new quantities.
- The doublet CENTER shift `eta_center` is already well predicted by geometry
  (R^2 = 0.86) and gains little from weighting (+0.07): the center is close to a
  Weyl/area response, consistent with known behaviour.

Therefore the gap marks are well explained by KNOWN eigenfunction-weighted
finite-rank theory, with a direct literature analog. The E3 condition "no direct
literature analog" FAILS. The correct status is **E2 KNOWN FINITE-RANK /
DISCREPANCY PHYSICS**: eigenfunction weighting adds the KNOWN matrix-element
structure over bare counting, not structure beyond existing theory. A candidate
for novelty (E3) would require reproducible structure in the marks that the
finite-rank + discrepancy prediction does NOT capture; none is demonstrated
here. No large pilot is warranted.
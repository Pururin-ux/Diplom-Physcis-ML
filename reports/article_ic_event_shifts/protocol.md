# Article-Ic frozen protocol: canonical event-resolved spectral shifts

Status: publicly timestamped prospective protocol for a REDEFINITION/CORRECTION
stage. Not a discovery preregistration. Pushed to the remote as a standalone
commit; SHA recorded before any result commit. Amendments only via dated
addenda pushed before the affected computation. Branch
`article-ic-event-resolved-spectral-shifts` from Article-Ib HEAD `1e59c30`.
Article-I/Ib/H/G/F files unchanged except additive correction records.

Central question: do the boundary events of a digital billiard form a canonical
eigenfunction-weighted marked spectral process carrying information BEYOND
ordinary lattice-point discrepancy, or is the whole remaining effect known
finite-rank graph perturbation + geometric discrepancy physics?

## Canonical object (frozen)

Digital domain `S(delta) = {r in Z^2 : F(r;delta) <= 1}`, area-preserving
a_x=a0/sqrt(1-delta), a_y=a0*sqrt(1-delta). Events at the discrete thresholds
where `S(delta)` changes. At event `e`: `S_e^- , S_e^+` (before/after),
`A_e = S_e^+ \ S_e^-` (added), `R_e = S_e^- \ S_e^+` (removed). A SWAP event
(|A_e|,|R_e|>0 with net 0) is a genuine event.

Marked spectral event (NO labels, transport, common space, or gauge):
`Delta E_{j,e} = E_j(S_e^+) - E_j(S_e^-)`, j=0,1,2,3;
`g(S)=E_2-E_1`, `Delta g_e = g(S_e^+)-g(S_e^-)`;
`c(S)=(E_1+E_2)/2`, `Delta c_e = c(S_e^+)-c(S_e^-)`.
Never called a derivative. Terms: spectral event shift / digital boundary-event
mark / event-resolved spectral jump / marked spectral jump process.

## Dimensionless additive normalization (frozen)

One fixed baseline scale per placement: `K_ref = E_0(S(0)) + 4`.
`eta_{j,e} = Delta E_{j,e}/K_ref`, `eta_{g,e}=Delta g_e/K_ref`,
`eta_{c,e}=Delta c_e/K_ref`. Do NOT divide a single event shift by an inter-event
spacing or by an arbitrary delta. Cumulative jump processes
`N(xi)=#{e:xi_e<=xi}`, `J_g(xi)=sum_{xi_e<=xi} eta_{g,e}`,
`V_g(xi)=sum eta_{g,e}^2`. Fixed-reference additivity (frozen identity):
`sum_{delta_e<=delta} eta_{g,e} = (g(S(delta))-g(S(0)))/K_ref` (telescoping).
Sensitivity controls: K_before and sqrt(K_-K_+); primary is K_ref.

## Exact event detection (frozen)

For each lattice site r in the bounding box, solve `F(r;delta)=1` for all roots
in the frozen delta range (analytic where possible, else bracketed root solver);
bundle roots within tolerance into one event; verify `S(delta_e^-) != S(delta_e^+)`
by set inequality (not site count); store full added/removed sets; cross-check
completeness against a very dense independent scan.

## Three separated objects (frozen; none called a derivative)

A. Relaxed spectral event shift `E_j(S+)-E_j(S-)` (primary).
B. Frozen-mode energy change (Rayleigh quotient of old mode in new domain),
   diagnostic.
C. Subspace rotation: projector distance `||P_+ - P_-||_F` and principal angles
   between the low-energy subspaces (mode-reorganization mark).

## Finite-rank theory (frozen scope)

Derive and toy-verify the bordered secular equation
`det(lam I - H+) = det(lam I - H-) det[lam I - C - B^T (lam I - H-)^{-1} B]`
for added-site bundles and the inverse Schur relation for removals; prove Cauchy
interlacing for induced-subgraph add/remove; state which shifts have fixed sign.
Schur complement is a textbook tool, not new; only its application to the mark
distribution could be of interest.

## Predictors and the discrepancy gate (frozen)

Model 0 (bare counting): event count, added/removed counts, row/column lengths,
orientation, curvature. Model 1 (eigenfunction-weighted finite-rank): boundary
mode amplitudes, changed-bond matrix elements, Schur self-energy
`B^T (lam I - H-)^{-1} B`, subspace rotation. Compare predictive quality for
`|eta_g|`, `eta_g`, `eta_c` with LEAVE-ONE-PLACEMENT-OUT evaluation (never random
splits of events from one placement). Outcome rule: if Model 1 does not
improve Model 0 substantially -> KNOWN DISCREPANCY EFFECT / STOP; if it improves
but only on this micro-pilot -> SPECTRAL MARK CANDIDATE / NOVELTY NOT ESTABLISHED.

## Grids (validation/event-mechanism micro-pilot only)

n in {2,4}; a0 in {24.3, 33.7}; placements 2 C4v, 2 Cs_axis, 4 C1;
xi = a0*delta in [0, 0.8]; EXACT enumeration of all events in that range;
a few low eigenvalues/modes per event. Forbidden: 64^2, full placement grid,
wide size series, manuscript, "search for a pretty effect".

## Frozen outcomes E1-E4 and stop/go A-D

E1 CANONICAL EVENT PROCESS VALIDATED (enumeration complete, telescoping holds,
marks basis/transport independent, finite-rank formulas reproduce mechanics) --
not yet novelty. E2 KNOWN FINITE-RANK/DISCREPANCY PHYSICS (shifts explained by
interlacing/Schur/discrepancy; weighting adds nothing) -> STOP. E3
EIGENFUNCTION-WEIGHTED EVENT STRUCTURE (bare counting insufficient; weights add
reproducible structure; no direct literature analog) -> POTENTIALLY NOVEL / NOT
ESTABLISHED. E4 EVENT OBJECT NOT USEFUL -> STOP.

Stop/go: A STOP (known/trivial or no structure); B METHOD NOTE ONLY (canonical
formulation useful, no separate novelty); C CONTINUE EVENT STATISTICS (weighted
process shows structure beyond bare discrepancy, novelty needs audit); D NEW
DIRECTION JUSTIFIED (concrete quantitative law absent from literature and
reproduced across sizes/placements). Do not choose the favorable option.

## Rules

Literature gate precedes computation (done). No "derivative" for any fixed-`a`
digital event object. No 64^2, no broad grid. All CSV reproducible.

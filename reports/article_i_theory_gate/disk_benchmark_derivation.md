# Continuum disk benchmark for the area-preserving elliptical deformation

Goal: derive from first principles (not assume) the first-order response of the
first-excited Dirichlet doublet of the disk under the Article-H area-preserving
deformation, and obtain the dimensionless coefficient that the Article-H
observable would report in the continuum limit. Independently verified
numerically (Bessel zeros + method of fundamental solutions). No lattice
eigensolves.

## Setup

Baseline domain: disk of radius `a0` (the n=2, r_AR=1 superellipse). Deformation
(Article-H, `src/article_g_signed_response.py:semi_axes`):
`a_x(delta) = a0/sqrt(1-delta)`, `a_y(delta) = a0*sqrt(1-delta)`, so the domain
is an ellipse of area `pi*a_x*a_y = pi*a0^2` (area exactly preserved).

Dirichlet Laplacian `-Delta psi = lambda psi`, `psi|_boundary = 0`. The
tight-binding kinetic scale maps as `E_kin = E+4 <-> lambda` near the band
bottom (`E+4 ≈ k^2`). Disk spectrum: ground `psi_0 = J0(j01 r/a0)`,
`lambda_0 = (j01/a0)^2`; first excited DOUBLET
`psi_{x,y} = c J1(j11 r/a0){cos phi, sin phi}`, `lambda_1 = (j11/a0)^2`,
with `j01 = 2.404825`, `j11 = 3.831706`.

## First-order boundary displacement

To first order in delta: `a_x ≈ a0(1+delta/2)`, `a_y ≈ a0(1-delta/2)`. The
boundary point at angle phi moves from `a0(cos phi, sin phi)` to
`(a0(1+delta/2)cos phi, a0(1-delta/2)sin phi)`, a displacement
`a0(delta/2)(cos phi, -sin phi)`. The outward normal on the circle is
`n = (cos phi, sin phi)`, so the normal displacement is

  V_n(phi) = a0 (delta/2) (cos^2 phi - sin^2 phi) = (a0 delta/2) cos 2phi.

This is a pure quadrupole (l=2) boundary perturbation.

## Hadamard shape derivative in the degenerate doublet

For a Dirichlet eigenpair with unit-normalized psi, the Hadamard formula gives
the boundary perturbation matrix in the degenerate subspace
(Sokolowski-Zolesio 1992; Suzuki-Tsuchiya 2024; Grinfeld 2010):

  W_{ij} = - integral_{boundary} (d_n psi_i)(d_n psi_j) V_n ds.

Normal derivatives on the circle: `d_n psi_{x,y} = A {cos phi, sin phi}` with
`A = c (j11/a0) J1'(j11) = c (j11/a0) J0(j11)` (since J1(j11)=0). Unit
normalization `integral psi_x^2 dA = 1` gives
`c^2 = 2/(pi a0^2 J0(j11)^2)`, hence `A^2 a0^2 = 2 j11^2/(pi a0^2)`.

With `ds = a0 dphi` and the angular integrals
`int cos^2 phi cos2phi dphi = +pi/2`, `int sin^2 phi cos2phi dphi = -pi/2`,
`int cos phi sin phi cos2phi dphi = 0`:

  W_xx = -A^2 a0^2 (delta/2)(pi/2) = - j11^2 delta/(2 a0^2),
  W_yy = +A^2 a0^2 (delta/2)(pi/2) = + j11^2 delta/(2 a0^2),
  W_xy = 0.

So the perturbation matrix is DIAGONAL in the {p_x, p_y} basis:

  W = (j11^2 delta / (2 a0^2)) * diag(-1, +1).

Eigenvalue slopes (basis-invariant pair):
  dlambda_x/ddelta = - j11^2/(2 a0^2)   (p_x, elongated along x, energy DOWN),
  dlambda_y/ddelta = + j11^2/(2 a0^2)   (p_y, energy UP).
Gap slope (invariant): d(lambda_y - lambda_x)/ddelta = j11^2/a0^2.

## Ground state and the moving denominator

The ground state is m=0 (phi-independent), so
`W_00 = -A0^2 int cos2phi ds proportional to int_0^{2pi} cos2phi dphi = 0`:
the ground eigenvalue has ZERO first-order change under the area-preserving
quadrupole deformation (consistent with Faber-Krahn: the disk is the fixed-area
minimizer, so dlambda_0/ddelta = 0 at the circle). Therefore the "own" (moving)
and "fixed" denominators coincide at first order.

## Dimensionless benchmark (what Article-H would report)

Article-H labels the baseline doublet by the M_x reflection: `-` = M_x-odd
(p_x), `+` = M_x-even (p_y). So `E_+ - E_-` maps to `lambda_y - lambda_x` and

  q_split(delta) = (lambda_y - lambda_x)/lambda_0 = (j11^2/a0^2) delta /
                   (j01^2/a0^2) = (j11^2/j01^2) delta,  q_split(0) = 0,

  **chih_split(disk, C4v, p_x/p_y labels) = j11^2/j01^2 = 2.538734 (POSITIVE).**

Sign/factor audit (explicitly checked):
- The coefficient is `j11^2/j01^2`, NOT its inverse (`j01^2/j11^2 = 0.394`),
  NOT `lambda_2/lambda_1 = j11^2/j01^2` of the SAME domain by accident: here it
  genuinely is the gap-slope over the ground scale.
- No spurious factor 2: the gap slope is `j11^2/a0^2`; each level moves by half
  of that; dividing the gap slope by `lambda_0 = j01^2/a0^2` gives exactly
  `j11^2/j01^2`.
- Sign is POSITIVE with the p_x=-, p_y=+ convention (M_x-odd is the lower
  branch). A GLOBAL label swap (+ <-> -) flips the sign to -2.5387; the
  magnitude 2.5387 and the unordered slope pair {-1.269, +1.269} are the
  invariants.
- The a0-dependence cancels: the dimensionless benchmark is scale-free.

## Independent numerical verification (continuum, no lattice)

Bessel arithmetic: `j11^2/j01^2 = 3.831706^2/2.404825^2 = 2.538734`.

Method of fundamental solutions on the ellipse `a_x=1/sqrt(1-delta)`,
`a_y=sqrt(1-delta)` (a0=1):

| delta | lambda_0 | lambda_1 | lambda_2 | gap | (gap/lambda_0)/delta |
|---|---|---|---|---|---|
| 0.00 | 5.78319 | 14.68197 | (14.68197) | 0 | - |
| 0.01 | 5.78346 | 14.60887 | 14.75643 | 0.14756 | 2.5514 |
| 0.02 | 5.78430 | 14.53640 | 14.83304 | 0.29663 | 2.5641 |
| 0.03 | 5.78572 | 14.46459 | 14.91185 | 0.44726 | 2.5768 |

Linear extrapolation delta->0: 2.5514 - 0.01*(1.27) = 2.5387, matching
`j11^2/j01^2`. lambda_0 changes only at O(delta^2) (5.78319 -> 5.78572),
confirming the zero first-order ground shift. The analytic benchmark is
therefore independently confirmed.

## Status of the benchmark

`chih_split(disk continuum) = +j11^2/j01^2 = 2.5387` is **KNOWN TEXTBOOK
PHYSICS** (Hadamard shape derivative of a degenerate Dirichlet eigenvalue +
the classical circular-membrane / small-eccentricity-ellipse splitting). It is
the reference against which any lattice number must be read. It may be used
downstream ONLY as this verified value, with the explicit p_x/p_y label
convention and the sign caveat above.

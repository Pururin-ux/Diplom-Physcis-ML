"""Article-I continuum disk benchmark for the area-preserving elliptical
deformation. See reports/article_i_theory_gate/disk_benchmark_derivation.md.

The first-excited Dirichlet doublet of the disk splits under the deformation
a_x = a0/sqrt(1-delta), a_y = a0*sqrt(1-delta) with the Hadamard slopes

    dlambda_x/ddelta = - j11^2/(2 a0^2)   (p_x, M_x-odd, lower branch)
    dlambda_y/ddelta = + j11^2/(2 a0^2)   (p_y, M_x-even, upper branch)

and ground-state first-order shift zero. The dimensionless Article-H
observable (p_x = '-', p_y = '+') is chih_split = j11^2/j01^2.
"""

from __future__ import annotations

from scipy.special import jn_zeros

J01 = float(jn_zeros(0, 1)[0])   # 2.404825557...
J11 = float(jn_zeros(1, 1)[0])   # 3.831705970...

# Dimensionless benchmark reported by Article-H's chih_split in the continuum,
# with the p_x = '-' (M_x-odd) / p_y = '+' (M_x-even) label convention.
DISK_CHIH_SPLIT = (J11 / J01) ** 2   # 2.538734...

# Basis-invariant pair of dimensionless level slopes {dlambda/ddelta / lambda0}.
DISK_SLOPE_PAIR = (-0.5 * DISK_CHIH_SPLIT, +0.5 * DISK_CHIH_SPLIT)


def gap_slope(a0: float) -> float:
    """d(lambda_y - lambda_x)/ddelta for the disk of radius a0 (= j11^2/a0^2)."""
    return J11 ** 2 / a0 ** 2


def dimensionless_split_slope() -> float:
    """chih_split(disk continuum) = j11^2 / j01^2 (scale-free)."""
    return DISK_CHIH_SPLIT

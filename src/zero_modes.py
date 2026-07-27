"""Zero-mode analysis for superelliptic tight-binding billiards.

The Hamiltonian is the one used throughout this project: square lattice,
onsite energy ``0``, nearest-neighbour hopping ``-1``, sites retained inside a
superellipse, open (hard-wall) boundaries.

Because the square lattice is bipartite and the model has only
nearest-neighbour hopping, ``H`` is chiral. In the sublattice basis

    H = [[0, T], [T^T, 0]]

with ``T`` the ``N_A x N_B`` integer hopping block. Rank-nullity then gives

    nullity(H) = N - 2 * rank(T) >= |N_A - N_B|,

which is the *sublattice-imbalance bound*. It follows from the chiral block
structure, not from Lieb's theorem (that one concerns the ground-state spin of
the Hubbard model). Modes in excess of the bound appear when ``T`` carries
extra rank deficiency; such states are known as supernumerary zero modes.

This module deliberately separates three notions of the zero-mode count:

- ``structural``: ``N - 2 * nu`` with ``nu`` the maximum bipartite matching.
  A lower bound on the algebraic nullity, fixed by the graph alone.
- ``exact``: ``N - 2 * rank_p(T)`` with the rank computed by Gaussian
  elimination over one or more finite fields. Integer arithmetic, no threshold.
- ``numerical``: eigenvalues of ``H`` below a tolerance. Convenient but
  threshold-dependent; kept only for cross-checking.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

# Primes chosen so that p**2 stays below the int64 ceiling (~9.22e18),
# which keeps the modular elimination free of overflow.
DEFAULT_PRIMES: tuple[int, ...] = (2147483647, 1000000007, 998244353)


def superellipse_sites(
    a: float,
    aspect_ratio: float,
    n: float,
    center: tuple[float, float] = (0.0, 0.0),
    theta: float = 0.0,
) -> np.ndarray:
    """Return the integer lattice sites inside a superellipse.

    Parameters
    ----------
    a
        Semi-axis along the shape's own x direction, in lattice units.
    aspect_ratio
        ``b / a``.
    n
        Superellipse exponent.
    center
        Shape centre in lattice coordinates. ``(0, 0)`` places it on a lattice
        site; fractional values change the registration of the boundary
        relative to the lattice.
    theta
        Rotation of the shape relative to the lattice axes, in radians.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(N, 2)`` with integer site coordinates.
    """
    if a <= 0 or aspect_ratio <= 0 or n <= 0:
        raise ValueError("a, aspect_ratio, and n must be positive.")

    b = a * aspect_ratio
    cx, cy = center
    reach = int(np.ceil(max(a, b) + abs(cx) + abs(cy))) + 2
    grid = np.arange(-reach, reach + 1)
    X, Y = np.meshgrid(grid, grid, indexing="ij")

    dx = X - cx
    dy = Y - cy
    if theta != 0.0:
        ct, st = np.cos(theta), np.sin(theta)
        dx, dy = ct * dx + st * dy, -st * dx + ct * dy

    inside = (np.abs(dx / a) ** n + np.abs(dy / b) ** n) <= 1.0
    return np.column_stack((X[inside], Y[inside])).astype(np.int64)


@dataclass(frozen=True)
class Blocks:
    """Bipartite decomposition of a site set."""

    sites: np.ndarray
    idx_a: np.ndarray
    idx_b: np.ndarray
    T: np.ndarray  # integer N_A x N_B hopping block, entries in {0, 1}

    @property
    def n_sites(self) -> int:
        return int(self.sites.shape[0])

    @property
    def n_a(self) -> int:
        return int(self.idx_a.size)

    @property
    def n_b(self) -> int:
        return int(self.idx_b.size)

    @property
    def imbalance(self) -> int:
        return abs(self.n_a - self.n_b)


def bipartite_blocks(sites: np.ndarray) -> Blocks:
    """Split sites by sublattice and build the integer hopping block ``T``.

    ``T`` holds the adjacency between the two sublattices with entries in
    ``{0, 1}``. The physical hopping is ``-1``; the overall sign is irrelevant
    for rank, nullity, and matching.
    """
    parity = (sites[:, 0] + sites[:, 1]) % 2
    idx_a = np.flatnonzero(parity == 0)
    idx_b = np.flatnonzero(parity == 1)

    position = {(int(x), int(y)): k for k, (x, y) in enumerate(sites)}
    row_of = {int(i): r for r, i in enumerate(idx_a)}
    col_of = {int(i): c for c, i in enumerate(idx_b)}

    T = np.zeros((idx_a.size, idx_b.size), dtype=np.int64)
    for r, i in enumerate(idx_a):
        x, y = int(sites[i, 0]), int(sites[i, 1])
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            j = position.get((x + ddx, y + ddy))
            if j is not None:
                T[r, col_of[int(j)]] = 1
    del row_of
    return Blocks(sites=sites, idx_a=idx_a, idx_b=idx_b, T=T)


def dense_hamiltonian(sites: np.ndarray) -> np.ndarray:
    """Dense tight-binding Hamiltonian with onsite 0 and hopping -1."""
    position = {(int(x), int(y)): k for k, (x, y) in enumerate(sites)}
    N = sites.shape[0]
    H = np.zeros((N, N))
    for (x, y), i in position.items():
        for ddx, ddy in ((1, 0), (0, 1)):
            j = position.get((x + ddx, y + ddy))
            if j is not None:
                H[i, j] = H[j, i] = -1.0
    return H


def rank_mod_p(matrix: np.ndarray, p: int) -> int:
    """Rank of an integer matrix over ``GF(p)`` by Gaussian elimination.

    Always a lower bound on the rank over the rationals, with equality unless
    ``p`` divides a relevant minor. Agreement across several primes therefore
    pins the rational rank in practice.
    """
    A = np.mod(matrix.astype(np.int64), p)
    n_rows, n_cols = A.shape
    rank = 0
    for col in range(n_cols):
        if rank >= n_rows:
            break
        nz = np.flatnonzero(A[rank:, col])
        if nz.size == 0:
            continue
        pivot = rank + int(nz[0])
        if pivot != rank:
            A[[rank, pivot]] = A[[pivot, rank]]
        A[rank] = (A[rank] * pow(int(A[rank, col]), p - 2, p)) % p
        below = np.flatnonzero(A[rank + 1 :, col])
        if below.size:
            rows = rank + 1 + below
            A[rows] = (A[rows] - A[rows, col][:, None] * A[rank]) % p
        rank += 1
    return rank


def exact_nullity(blocks: Blocks, primes: tuple[int, ...] = DEFAULT_PRIMES) -> dict:
    """Threshold-free nullity from the modular rank of ``T``.

    Returns the per-prime ranks so that disagreement between fields is visible
    rather than averaged away.
    """
    ranks = {p: rank_mod_p(blocks.T, p) for p in primes}
    rank = max(ranks.values())
    return {
        "exact_rank_T": rank,
        "exact_nullity": blocks.n_sites - 2 * rank,
        "rank_agrees_across_primes": len(set(ranks.values())) == 1,
        "ranks_by_prime": ranks,
    }


def matching_deficiency(blocks: Blocks) -> dict:
    """Structural nullity from the maximum bipartite matching.

    ``rank(T) <= term_rank(T) = nu``, so ``N - 2*nu`` is a lower bound on the
    algebraic nullity. Any gap between the two is an algebraic cancellation
    that the graph structure alone does not explain.
    """
    graph = csr_matrix(blocks.T)
    matched = maximum_bipartite_matching(graph, perm_type="column")
    nu = int(np.sum(matched >= 0))
    return {"max_matching": nu, "structural_nullity": blocks.n_sites - 2 * nu}


def numerical_nullity(H: np.ndarray, tol: float = 1e-8) -> dict:
    """Threshold-based nullity, retained only as a cross-check.

    Also reports the spectral gap that separates the counted modes from the
    rest, so that the threshold's safety margin is explicit.
    """
    w = np.sort(np.abs(np.linalg.eigvalsh(H)))
    count = int(np.sum(w < tol))
    largest_counted = float(w[count - 1]) if count else 0.0
    next_level = float(w[count]) if count < w.size else float("nan")
    return {
        "numerical_nullity": count,
        "largest_counted_abs_E": largest_counted,
        "next_level_abs_E": next_level,
    }


def null_space_density(H: np.ndarray, tol: float = 1e-8) -> np.ndarray:
    """Site-resolved density of the zero-energy subspace.

    Returns the diagonal of the orthogonal projector onto the kernel, i.e.
    ``sum_k |psi_k(i)|^2`` over any orthonormal basis of the kernel. This is
    basis-independent, so it is well defined despite the degeneracy.
    """
    w, V = np.linalg.eigh(H)
    kernel = V[:, np.abs(w) < tol]
    if kernel.size == 0:
        return np.zeros(H.shape[0])
    return np.einsum("ik,ik->i", kernel, kernel)


def localisation_metrics(sites: np.ndarray, density: np.ndarray) -> dict:
    """Where the zero-mode weight sits: sublattice, boundary, participation."""
    total = float(density.sum())
    if total <= 0:
        return {
            "sublattice_polarisation": float("nan"),
            "boundary_weight_fraction": float("nan"),
            "ipr": float("nan"),
            "corner_weight_fraction": float("nan"),
        }

    normalised = density / total
    parity = (sites[:, 0] + sites[:, 1]) % 2
    weight_a = float(normalised[parity == 0].sum())
    weight_b = float(normalised[parity == 1].sum())

    position = {(int(x), int(y)) for x, y in sites}
    coordination = np.array(
        [
            sum(
                ((int(x) + ddx, int(y) + ddy) in position)
                for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            for x, y in sites
        ]
    )
    boundary = coordination < 4

    return {
        "sublattice_polarisation": abs(weight_a - weight_b),
        "boundary_weight_fraction": float(normalised[boundary].sum()),
        "corner_weight_fraction": float(normalised[coordination <= 2].sum()),
        "ipr": float(np.sum(normalised**2)),
    }


def chiral_breaking_splitting(
    sites: np.ndarray,
    kind: str,
    strength: float,
    n_modes: int,
    seed: int = 0,
) -> dict:
    """Split the zero-mode manifold with a chirality-breaking perturbation.

    ``kind='onsite'`` adds uniform random onsite energies, which breaks chiral
    symmetry while keeping the lattice bipartite. ``kind='nnn'`` adds
    next-nearest-neighbour hopping, which destroys bipartiteness itself.
    """
    H = dense_hamiltonian(sites)
    rng = np.random.default_rng(seed)

    if kind == "onsite":
        H = H + np.diag(rng.uniform(-strength, strength, size=H.shape[0]))
    elif kind == "nnn":
        position = {(int(x), int(y)): k for k, (x, y) in enumerate(sites)}
        for (x, y), i in position.items():
            for ddx, ddy in ((1, 1), (1, -1)):
                j = position.get((x + ddx, y + ddy))
                if j is not None:
                    H[i, j] = H[j, i] = -strength
    else:
        raise ValueError("kind must be 'onsite' or 'nnn'.")

    w = np.sort(np.linalg.eigvalsh(H))
    middle = np.argsort(np.abs(w))[:n_modes]
    formerly_zero = np.sort(w[middle])
    return {
        "perturbation": kind,
        "strength": strength,
        "max_abs_shift": float(np.max(np.abs(formerly_zero))) if n_modes else 0.0,
        "manifold_width": (
            float(formerly_zero[-1] - formerly_zero[0]) if n_modes else 0.0
        ),
        "rms_shift": float(np.sqrt(np.mean(formerly_zero**2))) if n_modes else 0.0,
    }


def analyse(
    a: float,
    aspect_ratio: float,
    n: float,
    center: tuple[float, float] = (0.0, 0.0),
    theta: float = 0.0,
    exact: bool = True,
    numeric: bool = True,
    primes: tuple[int, ...] = DEFAULT_PRIMES,
) -> dict:
    """Full zero-mode record for one geometry."""
    sites = superellipse_sites(a, aspect_ratio, n, center=center, theta=theta)
    blocks = bipartite_blocks(sites)

    record: dict = {
        "a": a,
        "aspect_ratio": aspect_ratio,
        "n": n,
        "center_x": center[0],
        "center_y": center[1],
        "theta": theta,
        "N_sites": blocks.n_sites,
        "N_A": blocks.n_a,
        "N_B": blocks.n_b,
        "imbalance_bound": blocks.imbalance,
    }
    record.update(matching_deficiency(blocks))
    if exact:
        exact_result = exact_nullity(blocks, primes=primes)
        exact_result.pop("ranks_by_prime")
        record.update(exact_result)
    if numeric:
        record.update(numerical_nullity(dense_hamiltonian(sites)))
    return record

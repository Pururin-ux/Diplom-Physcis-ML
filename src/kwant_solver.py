"""Sparse Hamiltonian extraction and low-energy spectrum for the rectangular dot."""

from __future__ import annotations

import numpy as np
from scipy import sparse as sp
from scipy.sparse.linalg import eigsh

from .geometry import build_rectangular_dot


def hamiltonian_submatrix_sparse(Lx: int, Ly: int) -> sp.csr_matrix:
    """Return the sparse Hamiltonian submatrix for the ``Lx`` x ``Ly`` dot.

    Uses a finalized Kwant system and ``hamiltonian_submatrix(sparse=True)``.

    Parameters
    ----------
    Lx, Ly
        Rectangle size in lattice sites (passed to :func:`geometry.build_rectangular_dot`).

    Returns
    -------
    scipy.sparse.csr_matrix
        Real symmetric Hamiltonian in CSR format.
    """
    fsys = build_rectangular_dot(Lx, Ly)
    h = fsys.hamiltonian_submatrix(sparse=True)
    return h.tocsr()


def _as_sorted_real_finite(vals: np.ndarray) -> np.ndarray:
    """Validate real finite values and return them sorted ascending."""
    arr = np.asarray(vals)
    arr = np.real_if_close(arr)
    if np.iscomplexobj(arr):
        raise ValueError("Eigenvalues must be real for this closed Hermitian system.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Encountered non-finite eigenvalues.")
    out = np.asarray(arr, dtype=float)
    out.sort()
    return out


def lowest_four_energies(Lx: int, Ly: int) -> np.ndarray:
    """Compute the lowest four eigenenergies (or all levels if fewer than four sites).

    Uses :func:`scipy.sparse.linalg.eigsh` with ``which='SA'`` when the Hilbert space
    dimension is large enough for ``k=4``. For very small systems, ``eigsh`` cannot
    request four eigenpairs; in that case the full spectrum is obtained with
    :func:`numpy.linalg.eigh` and the lowest levels are selected.

    Parameters
    ----------
    Lx, Ly
        Rectangle size in lattice sites.

    Returns
    -------
    numpy.ndarray
        Up to four lowest energies, finite, real, sorted in nondecreasing order.
    """
    h = hamiltonian_submatrix_sparse(Lx, Ly)
    n = h.shape[0]
    k = min(4, n)

    if k == 0:
        return np.array([], dtype=float)

    if n < 5:
        vals = np.linalg.eigvalsh(h.toarray())[:k]
    else:
        vals, _ = eigsh(h, k=4, which="SA")
    return _as_sorted_real_finite(vals)

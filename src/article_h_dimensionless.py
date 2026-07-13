"""Article-H: dimensionless reanalysis of the Article-G signed response.

Pure post-processing of the frozen Article-G pilot CSVs. Restores the
Article-F normalization by (E0 + 4) that Article-G had dropped. No eigensolves.

Definitions (protocol.md, article_h_dimensionless_response):
  q_split(cfg)   = (Etil_+ - Etil_-) / (E0 + 4)      [tracked branches]
  q_pm(cfg)      = (Etil_pm - E0) / (E0 + 4)
  q_center(cfg)  = (mean(Etil_+, Etil_-) - E0) / (E0 + 4)
  chih_X         = ( q_X(delta) - q_X(0) ) / delta
  L_old          = (Sdelta_sorted/(E0d+4)) / delta
  B_baseline     = (S0_sorted/(E00+4)) / delta
  C_sorted_bc    = ( Sdelta_sorted/(E0d+4) - S0_sorted/(E00+4) ) / delta
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Canonical set of input columns that must be present and numeric.
NUMERIC_INPUT_FIELDS = (
    "delta", "E0_0", "Eminus_0", "Eplus_0", "E0_delta", "Eminus_delta",
    "Eplus_delta", "S0_sorted", "Sdelta_sorted",
)
# Fields that the audit flagged as INVALID and must never enter derived data.
FORBIDDEN_FIELDS = ("symmetry_class_delta", "cut_bonds")

DERIVED_FIELDS = (
    "shape_n", "scale_a0", "deformation_mode", "delta", "xi", "dx", "dy",
    "theta", "grid", "branch_status", "symmetry_class_0",
    "E0_0", "Eminus_0", "Eplus_0", "E0_delta", "Eminus_delta", "Eplus_delta",
    "raw_chi_minus", "raw_chi_plus", "raw_chi_center", "raw_chi_split",
    "q_minus_0", "q_plus_0", "q_center_0", "q_split_0",
    "q_minus_delta", "q_plus_delta", "q_center_delta", "q_split_delta",
    "dimless_chi_minus", "dimless_chi_plus", "dimless_chi_center",
    "dimless_chi_split", "normalized_sorted_raw", "normalized_baseline_term",
    "normalized_sorted_bc",
)


def _f(row, key):
    return float(row[key])


def derived_row(row: dict) -> dict:
    """Compute all Article-H dimensionless quantities for one input CSV row."""
    delta = _f(row, "delta")
    e00 = _f(row, "E0_0")
    em0 = _f(row, "Eminus_0")
    ep0 = _f(row, "Eplus_0")
    e0d = _f(row, "E0_delta")
    emd = _f(row, "Eminus_delta")
    epd = _f(row, "Eplus_delta")
    s0 = _f(row, "S0_sorted")
    sd = _f(row, "Sdelta_sorted")

    k0 = e00 + 4.0
    kd = e0d + 4.0

    q_minus_0 = (em0 - e00) / k0
    q_plus_0 = (ep0 - e00) / k0
    q_center_0 = (0.5 * (ep0 + em0) - e00) / k0
    q_split_0 = (ep0 - em0) / k0

    q_minus_delta = (emd - e0d) / kd
    q_plus_delta = (epd - e0d) / kd
    q_center_delta = (0.5 * (epd + emd) - e0d) / kd
    q_split_delta = (epd - emd) / kd

    out = {
        "shape_n": row["shape_n"], "scale_a0": row["scale_a0"],
        "deformation_mode": row["deformation_mode"], "delta": delta,
        "xi": _f(row, "xi"), "dx": _f(row, "dx"), "dy": _f(row, "dy"),
        "theta": _f(row, "theta"), "grid": row["placement_grid"],
        "branch_status": row["branch_status"],
        "symmetry_class_0": row["symmetry_class_0"],
        "E0_0": e00, "Eminus_0": em0, "Eplus_0": ep0,
        "E0_delta": e0d, "Eminus_delta": emd, "Eplus_delta": epd,
        "raw_chi_minus": _f(row, "chi_minus"),
        "raw_chi_plus": _f(row, "chi_plus"),
        "raw_chi_center": _f(row, "chi_center"),
        "raw_chi_split": _f(row, "chi_split"),
        "q_minus_0": q_minus_0, "q_plus_0": q_plus_0,
        "q_center_0": q_center_0, "q_split_0": q_split_0,
        "q_minus_delta": q_minus_delta, "q_plus_delta": q_plus_delta,
        "q_center_delta": q_center_delta, "q_split_delta": q_split_delta,
        "dimless_chi_minus": (q_minus_delta - q_minus_0) / delta,
        "dimless_chi_plus": (q_plus_delta - q_plus_0) / delta,
        "dimless_chi_center": (q_center_delta - q_center_0) / delta,
        "dimless_chi_split": (q_split_delta - q_split_0) / delta,
        "normalized_sorted_raw": (sd / kd) / delta,
        "normalized_baseline_term": (s0 / k0) / delta,
        "normalized_sorted_bc": (sd / kd - s0 / k0) / delta,
    }
    return out


def dimless_split_under_swap(drow: dict) -> float:
    """dimless_chi_split if the deformed endpoint assignment is swapped.

    Swapping Etil_-, Etil_+ flips the sign of q_split_delta; the baseline
    q_split_0 is unchanged (the swap is over the deformed endpoint only).
    """
    return (-drow["q_split_delta"] - drow["q_split_0"]) / drow["delta"]


def dimless_center_under_swap(drow: dict) -> float:
    """chih_center is invariant under the endpoint swap (sum unchanged)."""
    return drow["dimless_chi_center"]


def sha256_canonical(path) -> str:
    """SHA256 over LF-normalized bytes, for cross-platform (CRLF/LF) stability."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()

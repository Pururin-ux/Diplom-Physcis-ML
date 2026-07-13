"""Regression tests for Article-H dimensionless reanalysis (protocol section 15)."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

from src import article_h_dimensionless as h

PROJECT_ROOT = Path(__file__).resolve().parents[1]
G_MAIN = PROJECT_ROOT / "reports" / "article_g_signed_response" / "pilot_main_rows.csv"


def toy_row(**over):
    row = {
        "shape_n": "4.0", "scale_a0": "33.7", "deformation_mode": "area_preserving",
        "placement_grid": "16", "delta": "0.01", "xi": "0.337", "dx": "0.3",
        "dy": "0.1", "theta": "0.0", "branch_status": "OK",
        "symmetry_class_0": "C1",
        "E0_0": "-3.99", "Eminus_0": "-3.98", "Eplus_0": "-3.975",
        "E0_delta": "-3.985", "Eminus_delta": "-3.977", "Eplus_delta": "-3.970",
        "S0_sorted": "0.005", "Sdelta_sorted": "0.007",
        "chi_minus": "0.0", "chi_plus": "0.0", "chi_center": "0.0", "chi_split": "0.0",
    }
    row.update(over)
    return row


# 4. identity chih_split == chih_plus - chih_minus
def test_identity_split_equals_plus_minus():
    d = h.derived_row(toy_row())
    assert abs(d["dimless_chi_split"] - (d["dimless_chi_plus"] - d["dimless_chi_minus"])) < 1e-12


# 2. exact decomposition L_old = B_baseline + C_sorted_bc
def test_f_metric_decomposition():
    d = h.derived_row(toy_row())
    assert abs(d["normalized_sorted_raw"]
               - (d["normalized_baseline_term"] + d["normalized_sorted_bc"])) < 1e-9


# 1 & 3. exact recovery of the normalized sorted metric and signed response
def test_normalized_values_hand_computed():
    d = h.derived_row(toy_row())
    # k0=0.01, kd=0.015; q_split_0=0.5, q_split_delta=0.4666667
    assert abs(d["q_split_0"] - 0.5) < 1e-9
    assert abs(d["q_split_delta"] - (0.007 / 0.015)) < 1e-9
    assert abs(d["dimless_chi_split"] - ((0.007 / 0.015 - 0.5) / 0.01)) < 1e-9
    assert abs(d["normalized_sorted_raw"] - (0.007 / 0.015 / 0.01)) < 1e-9
    assert abs(d["normalized_baseline_term"] - (0.5 / 0.01)) < 1e-9


# 5. same-placement baseline (baseline uses E0_0, not E0_delta)
def test_baseline_uses_own_scale():
    d = h.derived_row(toy_row(E0_0="-3.99", E0_delta="-3.90"))
    assert abs(d["q_split_0"] - (0.005 / 0.01)) < 1e-9         # k0 = 0.01
    assert abs(d["q_split_delta"] - (0.007 / 0.10)) < 1e-9      # kd = 0.10


# 6. correct endpoint ground-state normalization (deformed uses E0_delta)
def test_endpoint_ground_state_normalization():
    d = h.derived_row(toy_row(E0_delta="-3.95"))  # kd = 0.05
    assert abs(d["q_center_delta"]
               - ((0.5 * (-3.970 + -3.977) - (-3.95)) / 0.05)) < 1e-9


# 7. OK / all / ambiguity worst-case bounds bracket the all-row mean
def test_ambiguity_bounds():
    from scripts.run_article_h_dimensionless_analysis import ambiguity_bounds
    ok = h.derived_row(toy_row(branch_status="OK"))
    amb = h.derived_row(toy_row(branch_status="AMBIGUOUS",
                                Eminus_delta="-3.972", Eplus_delta="-3.971"))
    b = ambiguity_bounds([ok, amb])
    assert b["mean_amb_lo"] <= b["mean_all"] <= b["mean_amb_hi"] + 1e-12
    # swap of the ambiguous row flips q_split_delta sign
    sw = h.dimless_split_under_swap(amb)
    assert abs(sw - ((-amb["q_split_delta"] - amb["q_split_0"]) / amb["delta"])) < 1e-12


# 9. forbidden field symmetry_class_delta never used
def test_no_symmetry_class_delta():
    assert "symmetry_class_delta" in h.FORBIDDEN_FIELDS
    d = h.derived_row(toy_row(symmetry_class_delta="C2v"))
    assert "symmetry_class_delta" not in d


# 10. forbidden field cut_bonds never used
def test_no_cut_bonds():
    assert "cut_bonds" in h.FORBIDDEN_FIELDS
    d = h.derived_row(toy_row(cut_bonds="99"))
    assert "cut_bonds" not in d
    assert all("cut_bonds" != f for f in h.DERIVED_FIELDS)


# 14. portable canonical hashing invariant to line endings
def test_canonical_hash_line_ending_invariant(tmp_path):
    lf = tmp_path / "lf.txt"; crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"a,b\n1,2\n3,4\n")
    crlf.write_bytes(b"a,b\r\n1,2\r\n3,4\r\n")
    assert h.sha256_canonical(lf) == h.sha256_canonical(crlf)


# --- tests that touch the frozen Article-G CSVs (read-only) ---

@pytest.mark.skipif(not G_MAIN.exists(), reason="Article-G pilot CSV absent")
def test_no_modification_of_raw_csv():
    before = h.sha256_canonical(G_MAIN)
    from scripts.run_article_h_dimensionless_analysis import build_derived
    build_derived()
    assert h.sha256_canonical(G_MAIN) == before


@pytest.mark.skipif(not G_MAIN.exists(), reason="Article-G pilot CSV absent")
def test_derived_row_count_exact():
    from scripts.run_article_h_dimensionless_analysis import build_derived
    assert len(build_derived()) == 20224


@pytest.mark.skipif(not G_MAIN.exists(), reason="Article-G pilot CSV absent")
def test_regression_against_audit_values():
    # audit: n=4, xi=0.4, area_preserving, dimensionless OK-mean
    # a0 = 24.3, 33.7, 48.2 -> -1.056, -1.415, -1.238
    from scripts.run_article_h_dimensionless_analysis import build_derived, sel, arr
    derived = build_derived()
    expected = {24.3: -1.056, 33.7: -1.415, 48.2: -1.238}
    for a0, exp in expected.items():
        v = arr(sel(derived, 4.0, a0, "area_preserving", "xi", 0.40), "dimless_chi_split")
        assert abs(float(v.mean()) - exp) < 0.03, f"a0={a0}: {v.mean():.4f} vs {exp}"


@pytest.mark.skipif(not G_MAIN.exists(), reason="Article-G pilot CSV absent")
def test_outputs_have_no_iid_pvalues():
    # 8. no p-value columns in any produced CSV
    import scripts.run_article_h_dimensionless_analysis as A
    A.main()
    banned = ("p_value", "pvalue", "p-value", "ks_p", "pval")
    for csvfile in A.H_DIR.glob("dimensionless_*.csv"):
        with open(csvfile) as fh:
            cols = [c.strip().lower() for c in fh.readline().split(",")]
        for c in cols:
            assert not any(b in c for b in banned), f"{csvfile.name}: {c}"

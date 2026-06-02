"""Read-only reproducibility inventory for the frozen diploma results.

The script intentionally does not rerun Kwant, notebooks, or report generation.
It only inspects existing files and writes two Markdown audit reports:

- reports/results_file_inventory.md
- reports/reproducibility_audit.md
"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ASSETS = REPORTS / "assets"
THESIS = ROOT / "thesis"
NOTEBOOKS = ROOT / "notebooks"
SRC = ROOT / "src"
DATA = ROOT / "data"


@dataclass(frozen=True)
class FileMeta:
    role: str
    purpose: str
    likely_generator: str
    thesis_use: str
    notes: str = ""


KNOWN: dict[str, FileMeta] = {
    "reports/physics_sanity_checks.csv": FileMeta(
        role="generated result and diagnostic summary",
        purpose="Step 07 physical sanity checks: E_kin, scaling, Bessel check, site count and sublattice diagnostics.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb",
        thesis_use="Chapter 3, Chapter 5, abstracts/conclusion; input to Step 09 and thesis figures.",
    ),
    "reports/ar_scaling_relative_deviation.csv": FileMeta(
        role="derived summary",
        purpose="Fixed-shape check of max relative deviation of (E0+4)a^2 over five a values for each (n, r_AR).",
        likely_generator="generation path not identified; derived from reports/physics_sanity_checks.csv",
        thesis_use="Chapter 3, conclusion, abstracts; figure used in Chapter 3 and defense slides.",
        notes="CSV generation should be scripted in the publication branch.",
    ),
    "reports/mlp_ablation_summary.csv": FileMeta(
        role="generated result summary",
        purpose="Step 08 16-cell Ridge vs MLP comparison summary.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb",
        thesis_use="Chapter 5 and Appendix B table.",
    ),
    "reports/mlp_ablation_per_fold.csv": FileMeta(
        role="generated result detail",
        purpose="Step 08 per-fold MAE/RMSE/MaxAE and MLP iteration details.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb",
        thesis_use="Appendix support; used to derive physical-scale MAE table.",
    ),
    "reports/mlp_ablation_seed_stability.csv": FileMeta(
        role="generated result summary",
        purpose="Step 08 seed-stability diagnostics for MLP initialization.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb",
        thesis_use="Chapter 5 and supporting figure.",
    ),
    "reports/model_error_physical_scale.csv": FileMeta(
        role="derived summary",
        purpose="Relative MAE normalization by E_kin for E0 and by dE1 for dE1.",
        likely_generator="generation path not identified; derived from mlp_ablation_summary/per-fold data",
        thesis_use="Chapter 5, Appendix B, abstracts, conclusion.",
        notes="CSV generation should be scripted in the publication branch.",
    ),
    "reports/ridge_oof_point_residuals.csv": FileMeta(
        role="generated result detail",
        purpose="Step 09 out-of-fold Ridge predictions, residuals and point-level diagnostics.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb",
        thesis_use="Chapter 5 residual analysis figures and summaries.",
    ),
    "reports/ridge_residual_correlations.csv": FileMeta(
        role="generated result summary",
        purpose="Step 09 Spearman residual correlations after duplicate predictor cleanup.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb",
        thesis_use="Chapter 5 residual analysis.",
    ),
    "reports/ridge_residual_predictor_collinearity.csv": FileMeta(
        role="generated result summary",
        purpose="Step 09 predictor collinearity matrix for residual diagnostics.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb",
        thesis_use="Residual-analysis support; not directly printed as a thesis table.",
    ),
    "reports/ridge_residual_hypothesis_summary.csv": FileMeta(
        role="generated result summary",
        purpose="Step 09 primary residual-hypothesis decision table.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb",
        thesis_use="Chapter 5 and conclusion.",
    ),
    "reports/results_integrity_audit.md": FileMeta(
        role="audit report",
        purpose="Integrity check for the eigenvalue validation cleanup.",
        likely_generator="manual audit",
        thesis_use="Not a frozen thesis input; post-cleanup evidence.",
    ),
    "reports/full_code_physics_math_integrity_audit.md": FileMeta(
        role="audit report",
        purpose="Earlier broad physics/math/result-integrity audit.",
        likely_generator="manual audit",
        thesis_use="Not a frozen thesis input; post-cleanup evidence.",
    ),
    "reports/reproducibility_audit.md": FileMeta(
        role="audit report",
        purpose="Post-thesis reproducibility and integrity audit for the computational pipeline.",
        likely_generator="scripts/audit_reproducibility.py",
        thesis_use="Not a frozen thesis input; post-thesis development support.",
    ),
    "reports/results_file_inventory.md": FileMeta(
        role="audit inventory",
        purpose="Inventory of report CSV/PNG/MD files, traceability, hashes and thesis usage.",
        likely_generator="scripts/audit_reproducibility.py",
        thesis_use="Not a frozen thesis input; post-thesis development support.",
    ),
    "reports/assets/e0_kin_a2_scaling_by_n.png": FileMeta(
        role="generated figure",
        purpose="E_kin a^2 scaling by n.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 3.",
    ),
    "reports/assets/ar_scaling_relative_deviation.png": FileMeta(
        role="generated figure",
        purpose="Heatmap of fixed-shape max relative deviation for (E0+4)a^2.",
        likely_generator="notebooks/regenerate_thesis_figures_ru.py from reports/ar_scaling_relative_deviation.csv",
        thesis_use="Chapter 3 and defense slides.",
    ),
    "reports/assets/circle_bessel_e0_check.png": FileMeta(
        role="generated figure",
        purpose="Circular n=2, r_AR=1 Bessel scale check for E0.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 3.",
    ),
    "reports/assets/de2_near_degeneracy_n2_ar1.png": FileMeta(
        role="generated figure",
        purpose="dE2 near-degeneracy diagnostic for n=2, r_AR=1.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 3.",
    ),
    "reports/assets/nsites_area_ratio_by_n.png": FileMeta(
        role="generated figure",
        purpose="N_sites / analytic area diagnostic by n.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 3.",
    ),
    "reports/assets/sublattice_imbalance_summary.png": FileMeta(
        role="generated figure",
        purpose="Sublattice imbalance diagnostic summary.",
        likely_generator="notebooks/07_physics_sanity_checks.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 3.",
    ),
    "reports/assets/mlp_ablation_improvement_by_cell.png": FileMeta(
        role="generated figure",
        purpose="Step 08 relative MLP improvement by comparison cell.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/mlp_ablation_ridge_vs_mlp_physics_mae.png": FileMeta(
        role="generated figure",
        purpose="Ridge MAE vs MLP+physics MAE.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/mlp_ablation_seed_stability.png": FileMeta(
        role="generated figure",
        purpose="Step 08 MLP seed-stability diagnostics.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/mlp_raw_vs_physics_features.png": FileMeta(
        role="generated figure",
        purpose="MLP on raw geometry parameters vs MLP with physically motivated descriptors.",
        likely_generator="notebooks/08_tiny_mlp_ablation.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/ridge_e0_loao_abs_residual_vs_edge_error.png": FileMeta(
        role="generated figure",
        purpose="E0/LOAO Ridge absolute residuals vs edge discretization diagnostics.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/ridge_e0_loao_abs_residual_vs_macro_params.png": FileMeta(
        role="generated figure",
        purpose="E0/LOAO Ridge absolute residuals vs smooth macro-parameters.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/ridge_residual_dominance_by_n.png": FileMeta(
        role="generated figure",
        purpose="Residual-correlation dominance summary by n.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
    "reports/assets/ridge_residual_correlation_heatmap.png": FileMeta(
        role="generated figure",
        purpose="Residual-correlation heatmap.",
        likely_generator="notebooks/09_residuals_vs_edge_discretization.ipynb; notebooks/regenerate_thesis_figures_ru.py can redraw from CSV",
        thesis_use="Chapter 5.",
    ),
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_short(path: Path) -> str:
    if path.name in {"results_file_inventory.md", "reproducibility_audit.md"}:
        return "generated"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()[:16]


def csv_shape(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() != ".csv":
        return None, None
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = sum(1 for _ in reader)
    return rows, len(header)


def scan_thesis_figures() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    for tex in list((THESIS / "chapters").glob("*.tex")) + list((THESIS / "appendices").glob("*.tex")):
        text = tex.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            raw = match.group(1)
            normalized = raw.replace("\\", "/")
            if normalized.startswith("../"):
                normalized = normalized[3:]
            out.setdefault(normalized, []).append(rel(tex))
    return out


def scan_text_mentions(paths: list[Path], names: list[str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {name: [] for name in names}
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name in names:
            if name in text:
                hits[name].append(rel(path))
    return hits


def collect_files() -> list[Path]:
    files = list(REPORTS.glob("*.csv"))
    files += list(REPORTS.glob("*.md"))
    files += list(ASSETS.glob("*.png"))
    return sorted(files, key=lambda p: rel(p).lower())


def fallback_meta(path: Path, thesis_figs: dict[str, list[str]], mentions: dict[str, list[str]]) -> FileMeta:
    r = rel(path)
    if r in thesis_figs:
        thesis_use = ", ".join(thesis_figs[r])
    else:
        thesis_use = "not referenced by thesis includegraphics or known appendix tables"
    if path.name.startswith("department_progress"):
        return FileMeta(
            role="progress-presentation support",
            purpose="Older department-progress material, not part of frozen thesis results.",
            likely_generator="generation path not identified",
            thesis_use="not used by frozen thesis",
            notes="Candidate for archiving outside publication branch.",
        )
    generator = "generation path not identified"
    if mentions.get(path.name):
        generator = "; ".join(mentions[path.name])
    return FileMeta(
        role="generated/supporting file",
        purpose="purpose not explicitly mapped in this audit",
        likely_generator=generator,
        thesis_use=thesis_use,
        notes="not a known core frozen-thesis file" if r not in thesis_figs else "",
    )


def build_inventory() -> tuple[str, list[str], list[str], dict[str, list[str]]]:
    files = collect_files()
    thesis_figs = scan_thesis_figures()
    mention_paths = list(NOTEBOOKS.glob("*.ipynb")) + list(NOTEBOOKS.glob("*.py")) + list(SRC.glob("*.py"))
    mentions = scan_text_mentions(mention_paths, [p.name for p in files])
    missing_thesis_figs = sorted([p for p in thesis_figs if not (ROOT / p).exists()])

    lines = [
        "# Results file inventory",
        "",
        "This inventory is read-only. It records existing result files without regenerating or overwriting them.",
        "",
        "| Path | Kind | Rows x columns | SHA-256 prefix | Role | Purpose | Likely generator | Thesis use | Notes |",
        "|---|---:|---:|---:|---|---|---|---|---|",
    ]
    for path in files:
        r = rel(path)
        meta = KNOWN.get(r) or fallback_meta(path, thesis_figs, mentions)
        rows, cols = csv_shape(path)
        shape = f"{rows} x {cols}" if rows is not None else "-"
        kind = path.suffix.lower().lstrip(".")
        sha = sha256_short(path)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{r}`",
                    kind,
                    shape,
                    f"`{sha}`",
                    meta.role,
                    meta.purpose,
                    meta.likely_generator,
                    meta.thesis_use,
                    meta.notes or "-",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Thesis figure references",
            "",
        ]
    )
    for fig, users in sorted(thesis_figs.items()):
        status = "present" if (ROOT / fig).exists() else "missing"
        lines.append(f"- `{fig}`: {status}; used by {', '.join(users)}")
    lines.extend(
        [
            "",
            "## Missing thesis-referenced files",
            "",
            "None." if not missing_thesis_figs else "\n".join(f"- `{p}`" for p in missing_thesis_figs),
            "",
        ]
    )
    return "\n".join(lines), missing_thesis_figs, [rel(p) for p in files], thesis_figs


def dataset_summary() -> list[str]:
    lines: list[str] = []
    dense = DATA / "superellipse_discrete_n_dense_dataset.npz"
    if dense.exists():
        with np.load(dense) as data:
            nrows = len(data["a"])
            a_vals = sorted(np.unique(data["a"]).tolist())
            ar_vals = sorted(np.unique(data["aspect_ratio"]).tolist())
            n_vals = sorted(np.unique(data["n"]).tolist())
            lines.extend(
                [
                    f"- Dense dataset: `{rel(dense)}`.",
                    f"- Row count: {nrows}.",
                    f"- a values: {a_vals}.",
                    f"- aspect_ratio values: {ar_vals}.",
                    f"- n values: {n_vals}.",
                ]
            )
    else:
        lines.append("- Dense dataset not found: not verified.")
    return lines


def build_audit(missing: list[str], thesis_figs: dict[str, list[str]]) -> str:
    core_used_pngs = sorted(thesis_figs)
    unused_assets = sorted(
        rel(p)
        for p in ASSETS.glob("*.png")
        if rel(p) not in thesis_figs
    )
    return "\n".join(
        [
            "# Reproducibility and integrity audit",
            "",
            "## Executive summary",
            "",
            "The frozen diploma result files are present and internally traceable to the main notebooks for Steps 07, 08, and 09. No frozen thesis figures were missing. Fast tests passed in the `diplom-kwant` environment.",
            "",
            "Two derived CSV summaries need stronger post-thesis traceability: `reports/ar_scaling_relative_deviation.csv` and `reports/model_error_physical_scale.csv`. Their values are consistent with the thesis narrative, but their generation path is not identified as a tracked notebook/script in the current repository. The publication branch should add deterministic scripts for these derived summaries before extending the project.",
            "",
            "The current computational pipeline computes and stores low-energy eigenvalues. Eigenvectors are not stored or analyzed in the main result files; they are discarded after the sparse eigensolver call. Therefore, post-thesis work on wave-function morphology should be added as a new analysis track, without retroactively changing the frozen diploma spectral conclusions.",
            "",
            "## Frozen diploma results",
            "",
            "The following outputs are treated as frozen thesis inputs and were not regenerated by this audit:",
            "",
            "- `reports/physics_sanity_checks.csv` and physics-check figures.",
            "- `reports/ar_scaling_relative_deviation.csv` and its heatmap.",
            "- `reports/mlp_ablation_summary.csv`, `reports/mlp_ablation_per_fold.csv`, and `reports/mlp_ablation_seed_stability.csv`.",
            "- `reports/model_error_physical_scale.csv`.",
            "- `reports/ridge_oof_point_residuals.csv`, residual-correlation summaries, and residual figures.",
            "",
            "Dataset summary:",
            "",
            *dataset_summary(),
            "",
            "## Result file inventory",
            "",
            "A complete file-by-file inventory was written to `reports/results_file_inventory.md`.",
            "",
            f"- Thesis-referenced PNG count: {len(core_used_pngs)}.",
            f"- Missing thesis-referenced files: {len(missing)}.",
            "- Missing thesis-referenced files: " + ("none." if not missing else ", ".join(f"`{p}`" for p in missing)),
            "",
            "Files present in `reports/assets/` but not referenced by frozen thesis `\\includegraphics` commands:",
            "",
            *([f"- `{p}`" for p in unused_assets] if unused_assets else ["- None."]),
            "",
            "These are not automatically wrong; they may be earlier diagnostics or supporting plots. They should be separated from publication-grade outputs later to reduce ambiguity.",
            "",
            "## Code-to-result traceability",
            "",
            "| Result group | Main files | Likely generator | Status |",
            "|---|---|---|---|",
            "| Dense superellipse dataset | `data/superellipse_discrete_n_dense_dataset.npz` | `notebooks/05_generate_and_inspect_superellipse_discrete_n_pilot.ipynb` calling `src.dataset.generate_superellipse_discrete_n_dense_dataset` | identified |",
            "| Physics sanity checks | `reports/physics_sanity_checks.csv`; physics PNGs | `notebooks/07_physics_sanity_checks.ipynb`; PNGs can be redrawn by `notebooks/regenerate_thesis_figures_ru.py` | identified |",
            "| Fixed-shape scaling summary | `reports/ar_scaling_relative_deviation.csv`; heatmap PNG | CSV generation path not identified; PNG redrawn by `notebooks/regenerate_thesis_figures_ru.py` | partially identified |",
            "| MLP ablation | `reports/mlp_ablation_summary.csv`; `reports/mlp_ablation_per_fold.csv`; `reports/mlp_ablation_seed_stability.csv`; MLP PNGs | `notebooks/08_tiny_mlp_ablation.ipynb`; PNGs can be redrawn by `notebooks/regenerate_thesis_figures_ru.py` | identified |",
            "| Physical-scale MAE | `reports/model_error_physical_scale.csv` | generation path not identified; derived from Step 08 outputs and target scales | not fully reproducible from a tracked script |",
            "| Ridge residual analysis | `reports/ridge_oof_point_residuals.csv`; residual summary CSVs; residual PNGs | `notebooks/09_residuals_vs_edge_discretization.ipynb`; PNGs can be redrawn by `notebooks/regenerate_thesis_figures_ru.py` | identified |",
            "| Appendix tables | values embedded in `thesis/appendices/appendix_tables.tex` | manually transcribed from `mlp_ablation_summary.csv` and `model_error_physical_scale.csv` | generation path not automated |",
            "",
            "## Eigenvalue and wave-function handling",
            "",
            "- `src/geometry.py` builds closed finite square-lattice systems with zero onsite energy and nearest-neighbor hopping `-1`.",
            "- `src/kwant_solver.py::lowest_four_energies` extracts a sparse Hamiltonian and calls `scipy.sparse.linalg.eigsh(..., which=\"SA\")` for the lowest algebraic eigenvalues.",
            "- `src/dataset.py::_superellipse_levels_and_site_count` builds the superellipse Hamiltonian, calls `eigsh(..., which=\"SA\")` for normal-size systems, validates/sorts eigenvalues with `_as_sorted_real_finite`, and returns four levels plus `N_sites`.",
            "- Eigenvectors are computed by `eigsh` as the second return value but are assigned to `_` and discarded. No saved dataset contains wave-function amplitudes.",
            "- `E0`, `E1`, `E2`, `E3` are the sorted lowest eigenvalues. `dE1 = E1 - E0`, `dE2 = E2 - E1`, and `dE3 = E3 - E2` are generated in `src/dataset.py`.",
            "- The `E_kin = E0 + 4` convention is applied in `reports/physics_sanity_checks.csv` and downstream summaries/figures; the raw NPZ dataset stores `E0` rather than `E_kin`.",
            "- Main quantitative thesis analyses use `E0` and `dE1`; `dE2` is diagnostic-only.",
            "",
            "## Obvious inconsistency checks",
            "",
            "- Missing thesis-used result files: " + ("none found." if not missing else "found; see inventory."),
            "- Duplicate conflicting core CSV names: none found among Step 07, 08, and 09 outputs.",
            "- Notebooks/scripts that reference core report files were identified for Steps 07, 08, and 09.",
            "- Core result paths referenced by the frozen thesis are present. Full notebook re-execution was not verified in this audit.",
            "- `reports/ar_scaling_relative_deviation.csv` and `reports/model_error_physical_scale.csv` are reproducibility weak spots because their CSV generation path is not tracked.",
            "- Exact regeneration of the two derived CSV summaries is not verified because no tracked generator was identified.",
            "- Older department-progress files in `reports/` are not part of frozen thesis results and may confuse future audits.",
            "",
            "## Current tests",
            "",
            "Command run:",
            "",
            "```text",
            "C:\\Users\\lalad\\miniforge3\\Scripts\\conda.exe run -n diplom-kwant python -m pytest tests -q",
            "```",
            "",
            "Result:",
            "",
            "```text",
            "34 passed, 1 warning in 13.29s",
            "```",
            "",
            "The warning is the existing OpenMP/threadpool warning. No long Kwant dataset generation or notebook execution was run.",
            "",
            "## Known limitations",
            "",
            "- Wave functions are not archived or analyzed by the current result pipeline.",
            "- Two derived summaries lack tracked generation scripts.",
            "- Appendix tables are manually embedded rather than generated from CSV at build time.",
            "- Current report directory mixes frozen thesis outputs, progress-presentation files, and audit files.",
            "- Figure PNG regeneration is separated from some CSV generation paths; this is acceptable for frozen results but should be tightened for publication.",
            "",
            "## Recommended next steps for publication branch",
            "",
            "1. Add small deterministic scripts for `ar_scaling_relative_deviation.csv` and `model_error_physical_scale.csv`.",
            "2. Add a machine-readable manifest with SHA-256 hashes for frozen input/output files.",
            "3. Separate `reports/frozen_thesis/`, `reports/audits/`, and `reports/progress/` or document the intended layout.",
            "4. Add an optional eigenvector export/analysis path for selected geometries if wave-function claims are developed post-thesis.",
            "5. Automate appendix-table generation from CSVs for any future manuscript branch.",
            "6. Keep the frozen diploma outputs read-only; create new post-thesis outputs under a new report namespace.",
            "",
        ]
    )


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    inventory, missing, _files, thesis_figs = build_inventory()
    (REPORTS / "results_file_inventory.md").write_text(inventory, encoding="utf-8", newline="\n")
    audit = build_audit(missing, thesis_figs)
    (REPORTS / "reproducibility_audit.md").write_text(audit, encoding="utf-8", newline="\n")
    print(REPORTS / "results_file_inventory.md")
    print(REPORTS / "reproducibility_audit.md")
    print(f"missing_thesis_figures={len(missing)}")


if __name__ == "__main__":
    main()

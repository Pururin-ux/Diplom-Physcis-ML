"""Regenerate thesis figures with Russian labels.

The script reads existing CSV reports only and rewrites PNG assets used in the
thesis. It does not change numerical data or run new spectral calculations.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ASSETS = REPORTS / "assets"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "mathtext.fontset": "dejavusans",
        "axes.unicode_minus": False,
        "figure.dpi": 120,
        "savefig.dpi": 300,
    }
)


def parse_value(value: str):
    if value == "":
        return np.nan
    if value == "True":
        return True
    if value == "False":
        return False
    try:
        return float(value)
    except ValueError:
        return value


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return [{key: parse_value(value) for key, value in row.items()} for row in csv.DictReader(fh)]


def group_by(rows: list[dict], *keys: str) -> dict[tuple, list[dict]]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    return groups


def column(rows: list[dict], key: str) -> list:
    return [row[key] for row in rows]


def sorted_rows(rows: list[dict], key: str) -> list[dict]:
    return sorted(rows, key=lambda row: row[key])


def isclose(value: float, target: float) -> bool:
    return bool(np.isclose(value, target))


def save(fig: plt.Figure, filename: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(ASSETS / filename, bbox_inches="tight")
    plt.close(fig)


def cell_label(row: dict) -> str:
    target = "$E_0$" if row["target"] == "E0" else "$dE_1$"
    return f"n={row['n']:.1f}\n{target}\n{row['protocol']}"


def sorted_summary(summary: list[dict]) -> list[dict]:
    return sorted(summary, key=lambda row: (row["n"], row["target"], row["protocol"]))


def plot_e0_scaling(phys: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    data = [row for row in phys if isclose(row["aspect_ratio"], 1.0)]
    for (n,), group in sorted(group_by(data, "n").items()):
        group = sorted_rows(group, "a")
        ax.plot(column(group, "a"), column(group, "scaled_E0"), marker="o", label=fr"$n={n:.1f}$")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"$E_{\mathrm{kin}}a^2$")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Класс формы")
    save(fig, "e0_kin_a2_scaling_by_n.png")


def plot_ar_scaling(ar: list[dict]) -> None:
    n_values = sorted({row["n"] for row in ar})
    r_values = sorted({row["r_AR"] for row in ar})
    lookup = {(row["n"], row["r_AR"]): row["max_relative_deviation_percent"] for row in ar}
    matrix = np.array([[lookup[(n, r)] for r in r_values] for n in n_values])

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    im = ax.imshow(matrix, aspect="auto", origin="lower")
    ax.set_xticks(np.arange(len(r_values)))
    ax.set_xticklabels([f"{value:.2f}" for value in r_values])
    ax.set_yticks(np.arange(len(n_values)))
    ax.set_yticklabels([f"{value:.1f}" for value in n_values])
    ax.set_xlabel(r"$r_{\mathrm{AR}}$")
    ax.set_ylabel(r"$n$")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$\eta$, %")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=8)
    save(fig, "ar_scaling_relative_deviation.png")


def plot_bessel(phys: list[dict]) -> None:
    data = sorted_rows(
        [row for row in phys if isclose(row["n"], 2.0) and isclose(row["aspect_ratio"], 1.0)],
        "a",
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(column(data, "a"), column(data, "E_kin"), marker="o", label=r"$E_{\mathrm{kin}}$")
    ax.plot(column(data, "a"), column(data, "E_Bessel"), marker="s", label="оценка Бесселя")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"Энергия, $|t|$")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, "circle_bessel_e0_check.png")


def plot_de2(phys: list[dict]) -> None:
    data = sorted_rows(
        [row for row in phys if isclose(row["n"], 2.0) and isclose(row["aspect_ratio"], 1.0)],
        "a",
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot(column(data, "a"), column(data, "dE2"), marker="o")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"$dE_2$, $|t|$")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.grid(True, alpha=0.3)
    save(fig, "de2_near_degeneracy_n2_ar1.png")


def plot_nsites_area(phys: list[dict]) -> None:
    data = [row for row in phys if isclose(row["aspect_ratio"], 1.0)]
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2), sharex=True)
    for (n,), group in sorted(group_by(data, "n").items()):
        group = sorted_rows(group, "a")
        label = fr"$n={n:.1f}$"
        axes[0].plot(column(group, "a"), column(group, "N_sites"), marker="o", label=label)
        axes[1].plot(column(group, "a"), column(group, "N_sites_over_area"), marker="o", label=label)
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$N_{\mathrm{sites}}$")
    axes[1].set_xlabel(r"$a$")
    axes[1].set_ylabel(r"$N_{\mathrm{sites}}/S_{\mathrm{an}}$")
    for ax in axes:
        ax.grid(True, alpha=0.3)
    axes[1].axhline(1.0, color="0.4", lw=1.0, ls="--", label="аналитическая площадь")
    axes[0].legend(title="Класс формы")
    save(fig, "nsites_area_ratio_by_n.png")


def plot_sublattice_imbalance(phys: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for (n,), group in sorted(group_by(phys, "n").items()):
        ax.scatter(column(group, "a"), [100 * value for value in column(group, "imbalance_ratio")], s=28, alpha=0.75, label=fr"$n={n:.1f}$")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel("Подрешёточный дисбаланс, %")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Класс формы", ncol=2)
    save(fig, "sublattice_imbalance_summary.png")


def plot_mlp_improvement(summary: list[dict]) -> None:
    data = sorted_summary(summary)
    x = np.arange(len(data))
    success_color = "#4C72B0"
    fail_color = "#B0B0B0"
    colors = [success_color if row["cell_success"] else fail_color for row in data]
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.bar(x, column(data, "improvement_percent"), color=colors)
    ax.axhline(15.0, color="0.25", lw=1.0, ls="--")
    ax.axhline(0.0, color="0.4", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([cell_label(row) for row in data], rotation=0, fontsize=8)
    ax.set_ylabel(r"$\Delta \mathrm{MAE}$, %")
    ax.legend(
        handles=[
            Patch(facecolor=success_color, label="успех по критерию"),
            Patch(facecolor=fail_color, label="критерий не выполнен"),
            Line2D([0], [0], color="0.25", lw=1.0, ls="--", label="порог 15%"),
        ]
    )
    save(fig, "mlp_ablation_improvement_by_cell.png")


def plot_ridge_vs_mlp(summary: list[dict]) -> None:
    data = sorted_summary(summary)
    x = np.arange(len(data))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.bar(x - width / 2, column(data, "ridge_mae"), width, label="гребневая регрессия")
    ax.bar(x + width / 2, column(data, "mlp_physics_mae_mean"), width, label="МП + физические признаки")
    ax.set_xticks(x)
    ax.set_xticklabels([cell_label(row) for row in data], rotation=0, fontsize=8)
    ax.set_ylabel(r"$\mathrm{MAE}$, $|t|$")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "mlp_ablation_ridge_vs_mlp_physics_mae.png")


def plot_seed_stability(summary: list[dict]) -> None:
    data = sorted_summary(summary)
    x = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.errorbar(
        x,
        column(data, "mlp_physics_mae_mean"),
        yerr=[2 * value for value in column(data, "mlp_physics_mae_se")],
        fmt="o",
        capsize=3,
        label="МП + физические признаки: среднее +/- 2SE",
    )
    ax.scatter(x, column(data, "ridge_mae"), marker="s", label="гребневая регрессия")
    ax.set_xticks(x)
    ax.set_xticklabels([cell_label(row) for row in data], rotation=0, fontsize=8)
    ax.set_ylabel(r"$\mathrm{MAE}$, $|t|$")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "mlp_ablation_seed_stability.png")


def plot_raw_vs_physics(summary: list[dict]) -> None:
    data = sorted_summary(summary)
    x = np.arange(len(data))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.bar(x - width / 2, column(data, "mlp_raw_mae_mean"), width, label="МП + исходные параметры")
    ax.bar(x + width / 2, column(data, "mlp_physics_mae_mean"), width, label="МП + физические признаки")
    ax.set_xticks(x)
    ax.set_xticklabels([cell_label(row) for row in data], rotation=0, fontsize=8)
    ax.set_ylabel(r"$\mathrm{MAE}$, $|t|$")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "mlp_raw_vs_physics_features.png")


def plot_residual_edge(resid: list[dict]) -> None:
    data = [row for row in resid if row["target"] == "E0" and row["protocol"] == "LOAO"]
    fig, ax = plt.subplots(figsize=(7.3, 4.5))
    for (n,), group in sorted(group_by(data, "n").items()):
        ax.scatter(column(group, "edge_area_error_abs"), column(group, "abs_residual"), s=28, alpha=0.75, label=fr"$n={n:.1f}$")
    ax.set_xlabel("Ошибка дискретизации площади")
    ax.set_ylabel(r"$|y_{\mathrm{pred}}-y_{\mathrm{true}}|$, $|t|$")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Класс формы")
    save(fig, "ridge_e0_loao_abs_residual_vs_edge_error.png")


def plot_residual_macro(resid: list[dict]) -> None:
    data = [row for row in resid if row["target"] == "E0" and row["protocol"] == "LOAO"]
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2), sharey=True)
    for (n,), group in sorted(group_by(data, "n").items()):
        label = fr"$n={n:.1f}$"
        axes[0].scatter(column(group, "a"), column(group, "abs_residual"), s=26, alpha=0.75, label=label)
        axes[1].scatter(column(group, "aspect_ratio"), column(group, "abs_residual"), s=26, alpha=0.75, label=label)
    axes[0].set_xlabel(r"$a$")
    axes[1].set_xlabel(r"$r_{\mathrm{AR}}$")
    axes[0].set_ylabel(r"$|y_{\mathrm{pred}}-y_{\mathrm{true}}|$, $|t|$")
    for ax in axes:
        ax.grid(True, alpha=0.3)
    axes[1].legend(title="Класс формы")
    save(fig, "ridge_e0_loao_abs_residual_vs_macro_params.png")


def plot_residual_dominance(hyp: list[dict]) -> None:
    data = sorted_rows([row for row in hyp if row["target"] == "E0" and row["protocol"] == "LOAO"], "n")
    x = np.arange(len(data))
    width = 0.38
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.bar(x - width / 2, column(data, "max_abs_rho_discretization"), width, label="дискретизационные диагностики")
    ax.bar(x + width / 2, column(data, "max_abs_rho_smooth"), width, label="гладкие параметры")
    ax.axhline(0.3, color="0.35", lw=1.0, ls="--", label="порог 0.3")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['n']:.1f}" for row in data])
    ax.set_xlabel(r"$n$")
    ax.set_ylabel(r"$|\rho|$")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "ridge_residual_dominance_by_n.png")


def plot_residual_corr_heatmap(corr: list[dict]) -> None:
    variable_order = ["edge_area_error_abs", "imbalance_ratio", "a", "aspect_ratio"]
    variable_labels = [
        "ошибка\nплощади",
        "подрешёточный\nдисбаланс",
        r"$a$",
        r"$r_{\mathrm{AR}}$",
    ]
    data = [row for row in corr if row["variable"] in variable_order]
    rows = []
    values = []
    for (target, protocol, n), group in sorted(group_by(data, "target", "protocol", "n").items()):
        rows.append(f"{target}, {protocol}, n={n:.1f}")
        row_values = []
        for variable in variable_order:
            matches = [row for row in group if row["variable"] == variable]
            row_values.append(matches[0]["abs_spearman_rho"] if matches else np.nan)
        values.append(row_values)
    matrix = np.array(values, dtype=float)
    fig, ax = plt.subplots(figsize=(7.5, 8.0))
    im = ax.imshow(matrix, aspect="auto", vmin=0, vmax=np.nanmax(matrix))
    ax.set_xticks(np.arange(len(variable_order)))
    ax.set_xticklabels(variable_labels)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$|\rho|$")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isfinite(matrix[i, j]):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=7)
    save(fig, "ridge_residual_correlation_heatmap.png")


def main() -> None:
    phys = read_rows(REPORTS / "physics_sanity_checks.csv")
    ar = read_rows(REPORTS / "ar_scaling_relative_deviation.csv")
    summary = read_rows(REPORTS / "mlp_ablation_summary.csv")
    resid = read_rows(REPORTS / "ridge_oof_point_residuals.csv")
    hyp = read_rows(REPORTS / "ridge_residual_hypothesis_summary.csv")
    corr = read_rows(REPORTS / "ridge_residual_correlations.csv")

    plot_e0_scaling(phys)
    plot_ar_scaling(ar)
    plot_bessel(phys)
    plot_de2(phys)
    plot_nsites_area(phys)
    plot_sublattice_imbalance(phys)
    plot_mlp_improvement(summary)
    plot_ridge_vs_mlp(summary)
    plot_seed_stability(summary)
    plot_raw_vs_physics(summary)
    plot_residual_edge(resid)
    plot_residual_macro(resid)
    plot_residual_dominance(hyp)
    plot_residual_corr_heatmap(corr)


if __name__ == "__main__":
    main()

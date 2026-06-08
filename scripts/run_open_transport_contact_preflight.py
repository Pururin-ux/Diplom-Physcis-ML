"""Run the Article D open-transport contact-coupling preflight."""

from __future__ import annotations

import csv
from pathlib import Path
import sys
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.open_transport_preflight import (  # noqa: E402
    A_VALUE,
    ASPECT_RATIO,
    ENERGY_MAX,
    ENERGY_MIN,
    N_ENERGIES,
    N_VALUES,
    PRIMARY_LEAD_WIDTHS,
    build_open_transport_system,
    build_straight_channel_system,
    classify_preflight,
    conductance_curve,
    extract_curve_metrics,
    feature_energies,
    features_align_with_mode_thresholds,
    lead_mode_thresholds,
    normalized_curve_distance,
    shift_rescale_distance,
    typical_shape_effect,
)


OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_d_open_transport"
FIGURE_DIR = OUTPUT_DIR / "figures"

CONDUCTANCE_COLUMNS = [
    "geometry_label",
    "n",
    "a",
    "rAR",
    "lead_width",
    "energy",
    "transmission",
    "conductance_spinless_units",
    "lead_mode_count_if_available",
]

FEATURE_COLUMNS = [
    "geometry_label",
    "n",
    "a",
    "rAR",
    "lead_width",
    "mean_G",
    "var_G",
    "integrated_G",
    "total_variation_G",
    "num_local_maxima",
    "num_local_minima",
    "resonance_candidate_energies",
    "antiresonance_candidate_energies",
    "notes",
]

BASELINE_COLUMNS = [
    "baseline_name",
    "comparison",
    "metric",
    "value",
    "killed_true_false",
    "notes",
]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write CSV rows with stable columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _geometry_label(n_value: float, lead_width: int) -> str:
    """Return a stable curve label."""
    return f"n{float(n_value):.1f}_W{int(lead_width)}"


def _plot_contact(curves: dict[tuple[float, int], np.ndarray], energies: np.ndarray) -> None:
    """Plot W=4 vs W=10 for n=2."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7.0, 4.2))
    for width in PRIMARY_LEAD_WIDTHS:
        plt.plot(energies, curves[(2.0, int(width))], label=f"n=2.0, W={width}", linewidth=1.3)
    plt.xlabel("Energy")
    plt.ylabel("G (spinless units)")
    plt.title("Contact preflight: W=4 vs W=10")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "contact_preflight_G_vs_E_W4_W10.png", dpi=180)
    plt.close()


def _plot_by_shape(curves: dict[tuple[float, int], np.ndarray], energies: np.ndarray, width: int) -> None:
    """Plot conductance by shape for one lead width."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7.0, 4.2))
    for n_value in N_VALUES:
        plt.plot(energies, curves[(float(n_value), int(width))], label=f"n={n_value}", linewidth=1.3)
    plt.xlabel("Energy")
    plt.ylabel("G (spinless units)")
    plt.title(f"Contact preflight: shape curves at W={width}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"contact_preflight_G_vs_E_by_shape_W{int(width)}.png", dpi=180)
    plt.close()


def _feature_row(
    label: str,
    n_value: float,
    lead_width: int,
    energies: np.ndarray,
    curve: np.ndarray,
    notes: str = "",
) -> dict[str, object]:
    """Build one feature CSV row."""
    metrics = extract_curve_metrics(energies, curve)
    maxima, minima = feature_energies(metrics, energies)
    return {
        "geometry_label": label,
        "n": float(n_value),
        "a": A_VALUE,
        "rAR": ASPECT_RATIO,
        "lead_width": int(lead_width),
        "mean_G": metrics.mean,
        "var_G": metrics.variance,
        "integrated_G": metrics.integrated,
        "total_variation_G": metrics.total_variation,
        "num_local_maxima": len(maxima),
        "num_local_minima": len(minima),
        "resonance_candidate_energies": ";".join(f"{value:.8g}" for value in maxima[:12]),
        "antiresonance_candidate_energies": ";".join(f"{value:.8g}" for value in minima[:12]),
        "notes": notes,
    }


def _append_curve_rows(
    out: list[dict[str, object]],
    label: str,
    n_value: float,
    lead_width: int,
    curve_rows: list[dict[str, object]],
) -> None:
    """Append conductance rows with geometry metadata."""
    for row in curve_rows:
        out.append(
            {
                "geometry_label": label,
                "n": float(n_value),
                "a": A_VALUE,
                "rAR": ASPECT_RATIO,
                "lead_width": int(lead_width),
                "energy": row["energy"],
                "transmission": row["transmission"],
                "conductance_spinless_units": row["conductance_spinless_units"],
                "lead_mode_count_if_available": row["lead_mode_count_if_available"],
            }
        )


def _mode_threshold_kill(features: list[dict[str, object]], energy_step: float) -> bool:
    """Return whether most feature energies are near lead mode thresholds."""
    hits = 0
    checks = 0
    for feature in features:
        width = int(feature["lead_width"])
        thresholds = lead_mode_thresholds(width)
        for field in ("resonance_candidate_energies", "antiresonance_candidate_energies"):
            values = [float(value) for value in str(feature[field]).split(";") if value]
            if not values:
                continue
            checks += 1
            if features_align_with_mode_thresholds(values, thresholds, tolerance=2.0 * float(energy_step)):
                hits += 1
    return checks > 0 and hits / checks >= 0.5


def _mean_straight_channel_distance(
    curves: dict[tuple[float, int], np.ndarray],
    straight_curves: dict[int, np.ndarray],
) -> float:
    """Return average distance between dot curves and their straight-channel baselines."""
    distances: list[float] = []
    for (n_value, width), curve in curves.items():
        del n_value
        distances.append(normalized_curve_distance(curve, straight_curves[int(width)]))
    return float(np.mean(distances)) if distances else float("inf")


def _typical_shift_rescale_shape_effect(curves: dict[tuple[float, int], np.ndarray], width: int) -> float:
    """Return mean pairwise shift/rescale distance among n curves for one width."""
    values: list[float] = []
    for left, right in ((1.2, 2.0), (1.2, 4.0), (2.0, 4.0)):
        values.append(shift_rescale_distance(curves[(left, int(width))], curves[(right, int(width))]))
    return float(np.mean(values))


def write_summary(path: Path, metadata: dict[str, object]) -> None:
    """Write the preflight Markdown summary."""
    lines = [
        "# Open Transport Contact Preflight Summary",
        "",
        "## Scope",
        "",
        "This is a contact-coupling preflight for a new open-transport direction.",
        "Closed-spectrum Path B is not continued. No FD continuum references,",
        "TB-vs-FD residuals, closed-spectrum shape contrast, ML, inverse design,",
        "Q/S objectives, magnetic ranking crossover, or thesis/diploma edits are",
        "used.",
        "",
        "## System Definition",
        "",
        "- square-lattice tight-binding model",
        "- onsite `0`, nearest-neighbor hopping `-1`",
        "- spinless two-terminal conductance convention: `G=T`",
        f"- superellipse dot: `a={A_VALUE}`, `rAR={ASPECT_RATIO}`",
        "- flat one-lattice-column contact slices at `x=+-a` define the strip-lead interface",
        "",
        "## Lead And Energy Definition",
        "",
        "- two symmetric square-lattice strip leads",
        "- lead widths tested: `W=4` and `W=10`",
        f"- energy window: `[{ENERGY_MIN}, {ENERGY_MAX}]`",
        f"- energy points: `{N_ENERGIES}`",
        "",
        "## Phase 0A: Contact-Width Result",
        "",
        f"- contact_effect_size, n=2.0 W4 vs W10: `{metadata['contact_effect_size']}`",
        f"- shift/rescale contact distance: `{metadata['contact_shift_rescale_distance']}`",
        f"- smatrix failure count: `{metadata['failure_count']}`",
        "",
        "## Phase 0B: Shape-Vs-Contact Comparison",
        "",
        f"- shape_effect_size_W4: `{metadata['shape_effect_size_w4']}`",
        f"- shape_effect_size_W10: `{metadata['shape_effect_size_w10']}`",
        f"- lead width dominates: `{metadata['contact_dominance_kills']}`",
        "",
        "## Kill Tests",
        "",
        f"- mode thresholds explain features: `{metadata['mode_threshold_kills']}`",
        f"- straight-channel baseline computed: `{metadata['straight_channel_computed']}`",
        f"- straight-channel mean distance: `{metadata['straight_channel_mean_distance']}`",
        f"- straight-channel baseline killed: `{metadata['straight_channel_kills']}`",
        f"- energy-shift/rescale collapse killed: `{metadata['energy_shift_kills']}`",
        "",
        "## Strongest Observed Feature",
        "",
        f"- `{metadata['strongest_feature']}`",
        "",
        "## Final Verdict",
        "",
        f"`{metadata['verdict']}`",
        "",
        "A larger open-transport shape scout is recommended only for",
        "`OPEN_TRANSPORT_PREFLIGHT_CONTACT_STABLE_PROMISING`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_preflight() -> dict[str, object]:
    """Run the full contact preflight and write outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    energies = np.linspace(ENERGY_MIN, ENERGY_MAX, N_ENERGIES)
    energy_step = float(energies[1] - energies[0])

    conductance_rows: list[dict[str, object]] = []
    feature_rows: list[dict[str, object]] = []
    baseline_rows: list[dict[str, object]] = []
    curves: dict[tuple[float, int], np.ndarray] = {}
    failure_count = 0

    for width in PRIMARY_LEAD_WIDTHS:
        for n_value in N_VALUES:
            label = _geometry_label(float(n_value), int(width))
            system = build_open_transport_system(float(n_value), int(width), A_VALUE, ASPECT_RATIO)
            rows, failures = conductance_curve(system, energies, int(width))
            failure_count += failures
            curve = np.array([float(row["conductance_spinless_units"]) for row in rows], dtype=float)
            curves[(float(n_value), int(width))] = curve
            _append_curve_rows(conductance_rows, label, float(n_value), int(width), rows)
            feature_rows.append(_feature_row(label, float(n_value), int(width), energies, curve, notes=f"smatrix_failures={failures}"))

    straight_curves: dict[int, np.ndarray] = {}
    straight_channel_computed = True
    straight_failures = 0
    for width in PRIMARY_LEAD_WIDTHS:
        system = build_straight_channel_system(int(width), A_VALUE)
        rows, failures = conductance_curve(system, energies, int(width))
        straight_failures += failures
        straight_curves[int(width)] = np.array([float(row["conductance_spinless_units"]) for row in rows], dtype=float)

    contact_effect = normalized_curve_distance(curves[(2.0, 4)], curves[(2.0, 10)])
    contact_shift = shift_rescale_distance(curves[(2.0, 4)], curves[(2.0, 10)])
    shape_effect_w4 = typical_shape_effect({n_value: curves[(n_value, 4)] for n_value in N_VALUES})
    shape_effect_w10 = typical_shape_effect({n_value: curves[(n_value, 10)] for n_value in N_VALUES})
    shift_shape_w4 = _typical_shift_rescale_shape_effect(curves, 4)
    shift_shape_w10 = _typical_shift_rescale_shape_effect(curves, 10)

    contact_dominance_kills = contact_effect >= shape_effect_w4 and contact_effect >= shape_effect_w10
    mode_threshold_kills = _mode_threshold_kill(feature_rows, energy_step)
    straight_distance = _mean_straight_channel_distance(curves, straight_curves)
    straight_channel_kills = straight_distance < 0.10
    energy_shift_kills = (
        min(shift_shape_w4, shift_shape_w10) < 0.25 * min(shape_effect_w4, shape_effect_w10)
        and min(shift_shape_w4, shift_shape_w10) < 0.05
    )
    numerical_instability = failure_count > 0.05 * (len(N_VALUES) * len(PRIMARY_LEAD_WIDTHS) * len(energies))
    verdict = classify_preflight(
        contact_effect,
        shape_effect_w4,
        shape_effect_w10,
        mode_threshold_kills,
        straight_channel_kills,
        energy_shift_kills,
        numerical_instability,
    )

    baseline_metrics = {
        "contact_width": {
            "comparison": "n=2.0 W4 vs W10",
            "raw_distance": contact_effect,
            "shift_rescale_distance": contact_shift,
            "killed": contact_dominance_kills,
        },
        "shape_W4": {
            "comparison": "n=1.2/2.0/4.0 at W=4",
            "raw_distance": shape_effect_w4,
            "shift_rescale_distance": shift_shape_w4,
            "killed": False,
        },
        "shape_W10": {
            "comparison": "n=1.2/2.0/4.0 at W=10",
            "raw_distance": shape_effect_w10,
            "shift_rescale_distance": shift_shape_w10,
            "killed": False,
        },
        "straight_channel": {
            "comparison": "all dot curves vs same-W straight channel",
            "raw_distance": straight_distance,
            "shift_rescale_distance": "",
            "killed": straight_channel_kills,
        },
        "lead_mode_threshold": {
            "comparison": "feature energies vs strip subband thresholds",
            "raw_distance": "",
            "shift_rescale_distance": "",
            "killed": mode_threshold_kills,
        },
    }
    for name, data in baseline_metrics.items():
        for metric_name in ("raw_distance", "shift_rescale_distance"):
            if data[metric_name] == "":
                continue
            baseline_rows.append(
                {
                    "baseline_name": name,
                    "comparison": data["comparison"],
                    "metric": metric_name,
                    "value": data[metric_name],
                    "killed_true_false": data["killed"],
                    "notes": "",
                }
            )
        if name == "lead_mode_threshold":
            baseline_rows.append(
                {
                    "baseline_name": name,
                    "comparison": data["comparison"],
                    "metric": "threshold_alignment",
                    "value": mode_threshold_kills,
                    "killed_true_false": data["killed"],
                    "notes": f"W4 thresholds={lead_mode_thresholds(4)}; W10 thresholds={lead_mode_thresholds(10)}",
                }
            )

    all_features = sorted(feature_rows, key=lambda row: float(row["total_variation_G"]), reverse=True)
    strongest = (
        f"{all_features[0]['geometry_label']} total_variation={all_features[0]['total_variation_G']}, "
        f"maxima={all_features[0]['resonance_candidate_energies']}, minima={all_features[0]['antiresonance_candidate_energies']}"
        if all_features
        else "none"
    )

    metadata = {
        "verdict": verdict,
        "contact_effect_size": contact_effect,
        "contact_shift_rescale_distance": contact_shift,
        "shape_effect_size_w4": shape_effect_w4,
        "shape_effect_size_w10": shape_effect_w10,
        "contact_dominance_kills": contact_dominance_kills,
        "mode_threshold_kills": mode_threshold_kills,
        "straight_channel_computed": straight_channel_computed,
        "straight_channel_mean_distance": straight_distance,
        "straight_channel_kills": straight_channel_kills,
        "energy_shift_kills": energy_shift_kills,
        "failure_count": failure_count,
        "straight_failures": straight_failures,
        "strongest_feature": strongest,
    }

    write_csv(OUTPUT_DIR / "contact_preflight_conductance.csv", conductance_rows, CONDUCTANCE_COLUMNS)
    write_csv(OUTPUT_DIR / "contact_preflight_features.csv", feature_rows, FEATURE_COLUMNS)
    write_csv(OUTPUT_DIR / "contact_preflight_baselines.csv", baseline_rows, BASELINE_COLUMNS)
    write_summary(OUTPUT_DIR / "contact_preflight_summary.md", metadata)
    _plot_contact(curves, energies)
    _plot_by_shape(curves, energies, 4)
    _plot_by_shape(curves, energies, 10)
    return metadata


def main() -> None:
    """Run and report the contact preflight."""
    start = perf_counter()
    metadata = run_preflight()
    runtime = perf_counter() - start
    print(f"verdict: {metadata['verdict']}")
    print(f"contact_effect_size: {metadata['contact_effect_size']}")
    print(f"shape_effect_size_W4: {metadata['shape_effect_size_w4']}")
    print(f"shape_effect_size_W10: {metadata['shape_effect_size_w10']}")
    print(f"mode_threshold_kills: {metadata['mode_threshold_kills']}")
    print(f"straight_channel_kills: {metadata['straight_channel_kills']}")
    print(f"energy_shift_kills: {metadata['energy_shift_kills']}")
    print(f"runtime_seconds: {runtime:.3f}")
    print(f"wrote: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

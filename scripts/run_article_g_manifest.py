"""Generate the Article-G run manifest (protocol section 14): environment,
versions, commit SHA, timestamps, and SHA256 of all result artifacts.
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"

ARTIFACTS = [
    "protocol.md", "smoke_report.md", "pilot_main_rows.csv",
    "pilot_conv_rows.csv", "pilot_aggregates.csv", "pilot_convergence.csv",
    "pilot_chi_split_distributions_xi0.4.csv", "analysis_summary.md",
    "pilot_log.txt",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def versions() -> dict:
    out = {"python": platform.python_version(), "platform": platform.platform()}
    for pkg in ("numpy", "scipy", "kwant"):
        try:
            mod = __import__(pkg)
            out[pkg] = getattr(mod, "__version__", "unknown")
        except Exception:  # noqa: BLE001
            out[pkg] = "not importable in this interpreter"
    return out


def git(*args) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=PROJECT_ROOT).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def main() -> None:
    lines = ["# Article-G run manifest (protocol section 14)", ""]
    lines.append(f"- generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- branch: {git('rev-parse', '--abbrev-ref', 'HEAD')}")
    lines.append(f"- commit: {git('rev-parse', 'HEAD')}")
    lines.append(f"- protocol commit on remote (frozen before results): 0fa6cbe")
    v = versions()
    lines.append("- environment (from the running interpreter):")
    for k, val in v.items():
        lines.append(f"  - {k}: {val}")
    lines.append("- exact commands:")
    lines.append("  - `python scripts/run_article_g_smoke.py`")
    lines.append("  - `python scripts/run_article_g_pilot.py`")
    lines.append("  - `python scripts/run_article_g_analysis.py`")
    lines.append("  - test suite: `python -m pytest tests -q`")
    lines.append("")
    lines.append("## SHA256 of artifacts")
    for name in ARTIFACTS:
        p = OUTPUT_DIR / name
        if p.exists():
            lines.append(f"- `{name}`: {sha256(p)}")
        else:
            lines.append(f"- `{name}`: MISSING")
    (OUTPUT_DIR / "run_manifest.md").write_text("\n".join(lines), encoding="utf-8")
    print("manifest written")


if __name__ == "__main__":
    main()

"""Article-H run manifest (protocol section 16): parent SHA, input/output
SHA256 (canonical LF bytes), versions, commands, no-eigensolve statement.
"""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.article_h_dimensionless import sha256_canonical  # noqa: E402

G_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"
H_DIR = PROJECT_ROOT / "reports" / "article_h_dimensionless_response"
INPUTS = ["pilot_main_rows.csv", "pilot_conv_rows.csv"]
OUTPUTS = [
    "protocol.md", "article_h_dimensionless_rows.csv",
    "dimensionless_statistics.csv", "dimensionless_conditional.csv",
    "dimensionless_convergence.csv", "dimensionless_n2_vs_n4.csv",
    "dimensionless_scaling.csv", "dimensionless_legacy_control.csv",
    "outcome_and_verdict.md",
]


def git(*a):
    try:
        return subprocess.check_output(["git", *a], cwd=PROJECT_ROOT).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def count_rows(path):
    with open(path) as fh:
        return sum(1 for _ in fh) - 1


def main():
    lines = ["# Article-H run manifest (protocol section 16)", ""]
    lines.append(f"- generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- branch: {git('rev-parse', '--abbrev-ref', 'HEAD')}")
    lines.append(f"- commit: {git('rev-parse', 'HEAD')}")
    lines.append("- source branch: article-g-signed-shape-response")
    lines.append("- exact parent SHA: 2744ef0cfecff1a7ef9f8b1fbdee80134800ad0b")
    lines.append("- frozen protocol commit (on remote before results): 29d5da0")
    lines.append("- NO new eigensolves were run; reanalysis of existing CSVs only.")
    lines.append("- hashing convention: SHA256 over LF-normalized bytes "
                 "(CRLF->LF), for cross-platform stability.")
    lines.append("")
    lines.append("## Environment (running interpreter)")
    lines.append(f"- python: {platform.python_version()}")
    for pkg in ("numpy", "scipy"):
        try:
            lines.append(f"- {pkg}: {__import__(pkg).__version__}")
        except Exception:  # noqa: BLE001
            lines.append(f"- {pkg}: unknown")
    lines.append("")
    lines.append("## Exact commands")
    lines.append("- `python -m pytest tests/test_article_h_dimensionless_analysis.py -q`")
    lines.append("- `python scripts/run_article_h_dimensionless_analysis.py`")
    lines.append("- `python scripts/run_article_h_manifest.py`")
    lines.append("")
    lines.append("## Inputs (read-only, canonical SHA256)")
    for name in INPUTS:
        p = G_DIR / name
        lines.append(f"- `{name}`: rows={count_rows(p)}, {sha256_canonical(p)}")
    lines.append("")
    lines.append("## Outputs (canonical SHA256)")
    for name in OUTPUTS:
        p = H_DIR / name
        if p.exists():
            extra = f", rows={count_rows(p)}" if name.endswith(".csv") else ""
            lines.append(f"- `{name}`: {sha256_canonical(p)}{extra}")
        else:
            lines.append(f"- `{name}`: MISSING")
    p = H_DIR / "article_h_dimensionless_rows.csv"
    if p.exists():
        lines.append("")
        lines.append(f"- derived-row count: {count_rows(p)} (expected 20224)")
    (H_DIR / "run_manifest.md").write_text("\n".join(lines), encoding="utf-8")
    print("manifest written")


if __name__ == "__main__":
    main()

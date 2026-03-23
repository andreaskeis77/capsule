#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _find_latest_run(base_dir: Path) -> Path:
    candidates = [p for p in base_dir.glob("run_*") if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No run_* directories found under {base_dir}")
    return sorted(candidates)[-1]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _render_summary(payload: dict, run_dir: Path) -> str:
    lines: list[str] = []
    lines.append("# CI Quality Gates Summary")
    lines.append("")
    lines.append(f"- Run directory: `{run_dir.as_posix()}`")
    result = payload.get("result", "UNKNOWN")
    lines.append(f"- Result: **{result}**")
    base_url = payload.get("base_url")
    if base_url:
        lines.append(f"- Base URL: `{base_url}`")
    lines.append("")

    steps = payload.get("steps", [])
    lines.append("| Step | Status | Return code | Duration (s) |")
    lines.append("| --- | --- | ---: | ---: |")
    for step in steps:
        lines.append(
            f"| {step['name']} | {step['status']} | {step['return_code']} | {step['duration_s']:.3f} |"
        )

    failures = [step for step in steps if step["status"] != "ok"]
    if failures:
        lines.append("")
        lines.append("## Failures")
        lines.append("")
        for step in failures:
            lines.append(f"- `{step['name']}` → `{step['log_file']}`")
    else:
        lines.append("")
        lines.append("## Result")
        lines.append("")
        lines.append("- All required quality gates passed.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render latest quality-gate summary for CI.")
    parser.add_argument(
        "--base-dir",
        default="docs/_ops/quality_gates",
        help="Directory containing run_* quality gate folders.",
    )
    parser.add_argument(
        "--write-github-summary",
        action="store_true",
        help="Write rendered markdown to GITHUB_STEP_SUMMARY when available.",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    run_dir = _find_latest_run(base_dir)
    summary_json = run_dir / "summary.json"
    if not summary_json.exists():
        raise FileNotFoundError(f"Missing summary.json in {run_dir}")

    payload = _read_json(summary_json)
    markdown = _render_summary(payload, run_dir)

    sys.stdout.write(markdown)

    if args.write_github_summary:
        gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if gh_summary:
            Path(gh_summary).write_text(markdown, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

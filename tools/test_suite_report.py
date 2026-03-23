#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MARKER_RE = re.compile(r"pytest\.mark\.([A-Za-z_][A-Za-z0-9_]*)")
TEST_FUNC_RE = re.compile(r"^\s*def\s+test_[A-Za-z0-9_]*\s*\(", re.MULTILINE)


def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(20):
        if (cur / ".git").exists() or (cur / "pytest.ini").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent.parent)
TESTS_DIR = REPO_ROOT / "tests"
OUT_DIR = REPO_ROOT / "docs" / "_ops" / "test_suite"


def repo_relative(path: Path, *, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def extract_test_file_summary(path: Path, *, repo_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    markers = sorted(set(MARKER_RE.findall(text)))
    return {
        "path": repo_relative(path, repo_root=repo_root),
        "test_functions": len(TEST_FUNC_RE.findall(text)),
        "markers": markers,
    }


def build_suite_report(*, tests_dir: Path = TESTS_DIR, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    files = sorted(tests_dir.rglob("test_*.py"))
    summaries = [extract_test_file_summary(path, repo_root=repo_root) for path in files]
    marker_usage: dict[str, int] = {}
    for entry in summaries:
        for marker in entry["markers"]:
            marker_usage[marker] = marker_usage.get(marker, 0) + 1

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tests_dir": repo_relative(tests_dir, repo_root=repo_root),
        "total_files": len(summaries),
        "total_test_functions": sum(entry["test_functions"] for entry in summaries),
        "marker_usage": dict(sorted(marker_usage.items())),
        "files": summaries,
    }


def write_report(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Test Suite Report",
        "",
        f"- Generated (UTC): {payload['generated_utc']}",
        f"- Tests dir: `{payload['tests_dir']}`",
        f"- Total files: **{payload['total_files']}**",
        f"- Total test functions: **{payload['total_test_functions']}**",
        "",
        "## Marker usage",
        "",
    ]
    if payload["marker_usage"]:
        for marker, count in payload["marker_usage"].items():
            lines.append(f"- `{marker}`: {count} files")
    else:
        lines.append("- No explicit pytest markers detected.")
    lines.extend([
        "",
        "## Files",
        "",
        "| File | Tests | Markers |",
        "| --- | ---: | --- |",
    ])
    for entry in payload["files"]:
        markers = ", ".join(entry["markers"]) if entry["markers"] else "-"
        lines.append(f"| `{entry['path']}` | {entry['test_functions']} | {markers} |")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize the test suite by file and marker.")
    parser.add_argument("--tests-dir", default=str(TESTS_DIR))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    tests_dir = Path(args.tests_dir)
    out_dir = Path(args.out_dir)
    repo_root = _find_repo_root(tests_dir)
    payload = build_suite_report(tests_dir=tests_dir, repo_root=repo_root)
    write_report(out_dir, payload)
    print(f"[OK] wrote test suite report: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from tools.reporting_common import render_table, to_repo_rel, utc_now_iso, write_json, write_markdown
except Exception:  # pragma: no cover
    from reporting_common import render_table, to_repo_rel, utc_now_iso, write_json, write_markdown  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = REPO_ROOT / "docs" / "_ops"
QUALITY_GATES_DIR = OPS_ROOT / "quality_gates"
RELEASES_DIR = OPS_ROOT / "releases"
INDEX_DIR = OPS_ROOT / "report_index"


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect_quality_gates(limit: int = 10) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not QUALITY_GATES_DIR.exists():
        return entries
    for run_dir in sorted((p for p in QUALITY_GATES_DIR.iterdir() if p.is_dir()), reverse=True)[:limit]:
        summary = _safe_json(run_dir / "summary.json")
        diagnosis = _safe_json(run_dir / "diagnosis.json")
        entries.append(
            {
                "run_dir": to_repo_rel(run_dir, REPO_ROOT),
                "status": summary.get("status") or ("FAIL" if summary.get("failed_required_steps") else "OK"),
                "failed_required_steps": summary.get("failed_required_steps", []),
                "failure_count": diagnosis.get("failure_count", 0),
                "generated_utc": summary.get("generated_utc"),
            }
        )
    return entries


def collect_releases(limit: int = 10) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not RELEASES_DIR.exists():
        return entries
    for release_dir in sorted((p for p in RELEASES_DIR.iterdir() if p.is_dir()), reverse=True)[:limit]:
        evidence = _safe_json(release_dir / "release_evidence.json")
        if not evidence:
            continue
        entries.append(
            {
                "release_dir": to_repo_rel(release_dir, REPO_ROOT),
                "release_id": evidence.get("release_id"),
                "commit": evidence.get("commit"),
                "quality_gate_status": evidence.get("quality_gate_status"),
                "generated_at_utc": evidence.get("generated_at_utc"),
            }
        )
    return entries


def build_index(limit: int = 10) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now_iso(),
        "quality_gates": collect_quality_gates(limit=limit),
        "releases": collect_releases(limit=limit),
    }


def write_index(payload: dict[str, Any]) -> tuple[Path, Path]:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    stamp = payload["generated_at_utc"].replace(":", "").replace("-", "")[:15]
    json_path = write_json(INDEX_DIR / f"ops_index_{stamp}.json", payload)
    lines = ["# Ops Report Index", "", f"- Generated (UTC): {payload['generated_at_utc']}", ""]
    lines.extend(["## Quality gates", ""])
    lines.extend(
        render_table(
            ["run_dir", "status", "failure_count", "failed_required_steps", "generated_utc"],
            [
                [
                    item["run_dir"],
                    item["status"],
                    item["failure_count"],
                    ", ".join(item["failed_required_steps"]),
                    item["generated_utc"],
                ]
                for item in payload["quality_gates"]
            ],
        )
        if payload["quality_gates"]
        else ["- None."]
    )
    lines.extend(["", "## Releases", ""])
    lines.extend(
        render_table(
            ["release_dir", "release_id", "commit", "quality_gate_status", "generated_at_utc"],
            [
                [
                    item["release_dir"],
                    item["release_id"],
                    item["commit"],
                    item["quality_gate_status"],
                    item["generated_at_utc"],
                ]
                for item in payload["releases"]
            ],
        )
        if payload["releases"]
        else ["- None."]
    )
    md_path = write_markdown(INDEX_DIR / f"ops_index_{stamp}.md", lines)
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an index over recent quality gate and release evidence artifacts.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = build_index(limit=args.limit)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    json_path, md_path = write_index(payload)
    print(f"[OK] ops report index written: {json_path}")
    print(f"[OK] ops report index written: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

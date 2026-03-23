from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.security_inventory import (
    REPO_ROOT,
    SECURITY_DIR,
    gather_security_inventory,
)

QUALITY_GATES_DIR = REPO_ROOT / "docs" / "_ops" / "quality_gates"
RELEASES_DIR = REPO_ROOT / "docs" / "_ops" / "releases"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _latest_ok_summary(directory: Path) -> dict[str, Any] | None:
    if not directory.exists():
        return None
    summaries: list[tuple[str, dict[str, Any], Path]] = []
    for child in sorted(directory.glob("run_*")):
        summary_path = child / "summary.json"
        if not summary_path.exists():
            continue
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        summaries.append((child.name, payload, child))
    ok = [item for item in summaries if item[1].get("status") == "OK"]
    if not ok:
        return None
    name, payload, child = ok[-1]
    return {
        "run_name": name,
        "path": child.as_posix(),
        "status": payload.get("status"),
    }


def _latest_release_evidence(directory: Path) -> dict[str, Any] | None:
    if not directory.exists():
        return None
    candidates = sorted(directory.glob("release_evidence_*.json"))
    if not candidates:
        return None
    latest = candidates[-1]
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return {
        "path": latest.as_posix(),
        "release_id": payload.get("release_id"),
        "quality_gate_status": payload.get("quality_gate_status"),
    }


def build_security_hygiene_payload(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    inventory = gather_security_inventory(repo_root)
    latest_quality = _latest_ok_summary(repo_root / "docs" / "_ops" / "quality_gates")
    latest_release = _latest_release_evidence(repo_root / "docs" / "_ops" / "releases")

    warnings: list[str] = []
    if not inventory["required_controls_present"]:
        warnings.append("One or more required security controls are missing.")
    if inventory["requirements"]["unpinned"] > 0:
        warnings.append("One or more Python dependencies are not pinned.")
    if latest_quality is None:
        warnings.append("No successful quality gate run was found.")

    status = "OK" if not warnings else "WARN"
    return {
        "generated_at": _utc_now_iso(),
        "status": status,
        "warnings": warnings,
        "inventory": inventory,
        "latest_quality_gates": latest_quality,
        "latest_release_evidence": latest_release,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Security Hygiene Report",
        "",
        f"Generated at: {payload['generated_at']}",
        f"Status: {payload['status']}",
        "",
        "## Summary",
        "",
        f"- Required controls present: {payload['inventory']['required_controls_present']}",
        f"- Optional controls present: {payload['inventory']['optional_controls_present']}/{payload['inventory']['optional_controls_total']}",
        f"- Pinned dependencies: {payload['inventory']['requirements']['pinned']}/{payload['inventory']['requirements']['total']}",
        "",
    ]
    if payload["latest_quality_gates"]:
        lines.extend([
            "## Latest Successful Quality Gates",
            "",
            f"- Run: `{payload['latest_quality_gates']['run_name']}`",
            f"- Path: `{payload['latest_quality_gates']['path']}`",
            "",
        ])
    if payload["latest_release_evidence"]:
        lines.extend([
            "## Latest Release Evidence",
            "",
            f"- Release ID: `{payload['latest_release_evidence']['release_id']}`",
            f"- Path: `{payload['latest_release_evidence']['path']}`",
            "",
        ])
    lines.append("## Warnings")
    lines.append("")
    if payload["warnings"]:
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def write_report(payload: dict[str, Any], output_dir: Path = SECURITY_DIR) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "security_hygiene_latest.json"
    md_path = output_dir / "security_hygiene_latest.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lightweight security hygiene report.")
    parser.add_argument("--write", action="store_true", help="Write the report into docs/_ops/security.")
    args = parser.parse_args()
    payload = build_security_hygiene_payload()
    if args.write:
        json_path, md_path = write_report(payload)
        print(f"[OK] wrote security hygiene report: {json_path}")
        print(f"[OK] wrote security hygiene report: {md_path}")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

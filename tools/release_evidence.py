from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
QUALITY_GATES_DIR = REPO_ROOT / "docs" / "_ops" / "quality_gates"
RELEASES_DIR = REPO_ROOT / "docs" / "_ops" / "releases"
BRANCH_PROTECTION_CONTRACT = REPO_ROOT / ".github" / "branch-protection.required-checks.json"


@dataclass(frozen=True)
class GateRun:
    run_dir: Path
    summary_json: Path
    summary: dict[str, Any]


def _iter_run_dirs() -> list[Path]:
    if not QUALITY_GATES_DIR.exists():
        return []
    return sorted(
        [p for p in QUALITY_GATES_DIR.iterdir() if p.is_dir() and p.name.startswith("run_")],
        key=lambda p: p.name,
    )


def _repo_relative_posix(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def find_latest_successful_gate_run() -> GateRun:
    latest_ok: GateRun | None = None
    for run_dir in _iter_run_dirs():
        summary_json = run_dir / "summary.json"
        if not summary_json.exists():
            continue
        try:
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if str(summary.get("status", "")).upper() == "OK":
            latest_ok = GateRun(run_dir=run_dir, summary_json=summary_json, summary=summary)
    if latest_ok is None:
        raise FileNotFoundError("No successful quality gate run found in docs/_ops/quality_gates.")
    return latest_ok


def read_branch_protection_contract() -> dict[str, Any]:
    return json.loads(BRANCH_PROTECTION_CONTRACT.read_text(encoding="utf-8"))


def resolve_commit() -> str:
    return os.getenv("GITHUB_SHA") or os.getenv("CI_COMMIT_SHA") or os.getenv("CAPSULE_COMMIT") or "UNKNOWN"


def build_release_payload(release_id: str | None = None) -> dict[str, Any]:
    gate_run = find_latest_successful_gate_run()
    contract = read_branch_protection_contract()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return {
        "release_id": release_id or f"release-{timestamp}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "commit": resolve_commit(),
        "quality_gate_status": gate_run.summary.get("status", "UNKNOWN"),
        "quality_gate_run_dir": _repo_relative_posix(gate_run.run_dir),
        "quality_gate_summary_json": _repo_relative_posix(gate_run.summary_json),
        "required_status_checks": contract.get("required_status_checks", []),
        "required_review_count": contract.get("required_review_count"),
        "require_code_owner_reviews": contract.get("require_code_owner_reviews"),
        "require_conversation_resolution": contract.get("require_conversation_resolution"),
    }


def write_release_evidence(payload: dict[str, Any]) -> Path:
    release_id = str(payload["release_id"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = RELEASES_DIR / f"{release_id}_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    (out_dir / "release_evidence.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md = [
        f"# Release Evidence: {release_id}",
        "",
        f"- Generated at (UTC): {payload['generated_at_utc']}",
        f"- Commit: {payload['commit']}",
        f"- Quality gate status: {payload['quality_gate_status']}",
        f"- Quality gate run folder: `{payload['quality_gate_run_dir']}`",
        f"- Quality gate summary json: `{payload['quality_gate_summary_json']}`",
        "",
        "## Required checks contract",
        *(f"- {name}" for name in payload["required_status_checks"]),
        "",
        f"- Required review count: {payload['required_review_count']}",
        f"- Require code-owner reviews: {payload['require_code_owner_reviews']}",
        f"- Require conversation resolution: {payload['require_conversation_resolution']}",
        "",
    ]
    (out_dir / "release_evidence.md").write_text("\n".join(md), encoding="utf-8")
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release evidence from the latest successful quality gate run.")
    parser.add_argument("--release-id", default=None, help="Optional stable release identifier.")
    args = parser.parse_args()

    payload = build_release_payload(release_id=args.release_id)
    out_dir = write_release_evidence(payload)
    print(f"[OK] release evidence written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

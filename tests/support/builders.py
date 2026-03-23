from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StepSummary:
    name: str
    status: str = "ok"
    returncode: int = 0
    duration_s: float = 0.1
    log_file: str = "step.log"
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "returncode": self.returncode,
            "duration_s": self.duration_s,
            "log_file": self.log_file,
            "required": self.required,
            "command": [],
        }


def repo_relative(path: str | Path) -> str:
    return str(Path(path)).replace("\\", "/")


def build_quality_gate_summary(
    *,
    status: str = "OK",
    failed_required_steps: list[str] | None = None,
    steps: list[StepSummary] | None = None,
    repo_root: str = ".",
    base_url: str = "http://127.0.0.1:8765",
    server_started: bool = False,
) -> dict[str, Any]:
    step_payload = [step.to_dict() for step in (steps or [])]
    failed = failed_required_steps or []
    return {
        "generated_utc": "2026-03-22T00:00:00+00:00",
        "repo_root": repo_root,
        "base_url": base_url,
        "server_started": server_started,
        "steps": step_payload,
        "failed_required_steps": failed,
        "status": status,
    }


def build_branch_protection_contract(
    *,
    required_status_checks: list[str] | None = None,
    required_review_count: int = 1,
    require_code_owner_reviews: bool = True,
    require_conversation_resolution: bool = True,
) -> dict[str, Any]:
    return {
        "required_status_checks": required_status_checks or ["quality-gates / quality-gates"],
        "required_review_count": required_review_count,
        "require_code_owner_reviews": require_code_owner_reviews,
        "require_conversation_resolution": require_conversation_resolution,
    }


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_quality_gate_run(run_dir: Path, *, summary: dict[str, Any]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "summary.json", summary)
    status = summary.get("status", "UNKNOWN")
    (run_dir / "summary.md").write_text(f"# Quality Gates Summary\n\n- Status: {status}\n", encoding="utf-8")
    return run_dir

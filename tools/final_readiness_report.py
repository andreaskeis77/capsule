from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.final_repo_baseline import REPO_ROOT, build_baseline_payload

QUALITY_GATES_DIR = REPO_ROOT / "docs" / "_ops" / "quality_gates"
RELEASES_DIR = REPO_ROOT / "docs" / "_ops" / "releases"
READINESS_DIR = REPO_ROOT / "docs" / "_ops" / "final_readiness"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rel_posix(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _latest_successful_quality_gate(directory: Path = QUALITY_GATES_DIR) -> tuple[Path | None, dict[str, Any] | None]:
    if not directory.exists():
        return None, None
    candidates = sorted([path for path in directory.glob("run_*") if path.is_dir()])
    for run_dir in reversed(candidates):
        summary = run_dir / "summary.json"
        if not summary.exists():
            continue
        try:
            payload = json.loads(summary.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("status") == "OK":
            return run_dir, payload
    return None, None


def _latest_release_evidence(directory: Path = RELEASES_DIR) -> tuple[Path | None, dict[str, Any] | None]:
    if not directory.exists():
        return None, None
    candidates = sorted(directory.glob("release_*.json"))
    if not candidates:
        return None, None
    latest = candidates[-1]
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return latest, None
    return latest, payload


def compute_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    top_ok = all(payload["baseline"]["top_level_contract"].values())
    docs_ok = payload["baseline"]["docs"]["present_count"] >= payload["baseline"]["docs"]["expected_count"] - 1
    qg_ok = payload["quality_gates"]["status"] == "OK"
    release_evidence_present = payload["release_evidence"]["present"]

    readiness = {
        "structure_ready": top_ok,
        "documentation_ready": docs_ok,
        "quality_gate_ready": qg_ok,
        "release_evidence_present": release_evidence_present,
    }
    readiness["overall_ready"] = all(
        [
            readiness["structure_ready"],
            readiness["quality_gate_ready"],
            readiness["release_evidence_present"],
        ]
    )
    return readiness


def build_readiness_payload(root: Path = REPO_ROOT) -> dict[str, Any]:
    baseline = build_baseline_payload(root)
    qg_dir, qg_summary = _latest_successful_quality_gate(root / "docs" / "_ops" / "quality_gates")
    rel_path, rel_payload = _latest_release_evidence(root / "docs" / "_ops" / "releases")

    payload = {
        "generated_at": _iso_now(),
        "repo_root": root.as_posix(),
        "baseline": baseline,
        "quality_gates": {
            "status": (qg_summary or {}).get("status", "MISSING"),
            "latest_successful_run_dir": _rel_posix(qg_dir, root) if qg_dir else None,
        },
        "release_evidence": {
            "present": rel_path is not None,
            "latest_file": _rel_posix(rel_path, root) if rel_path else None,
            "release_id": (rel_payload or {}).get("release_id"),
        },
    }
    payload["readiness"] = compute_readiness(payload)
    return payload


def _markdown(payload: dict[str, Any]) -> str:
    readiness = payload["readiness"]
    lines = [
        "# Final Readiness Report",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Latest successful quality gate: `{payload['quality_gates']['latest_successful_run_dir']}`",
        f"- Release evidence present: `{payload['release_evidence']['present']}`",
        "",
        "## Readiness",
        "",
        f"- Structure ready: `{readiness['structure_ready']}`",
        f"- Documentation ready: `{readiness['documentation_ready']}`",
        f"- Quality gate ready: `{readiness['quality_gate_ready']}`",
        f"- Release evidence present: `{readiness['release_evidence_present']}`",
        f"- Overall ready: `{readiness['overall_ready']}`",
        "",
        "## Baseline Summary",
        "",
        f"- ADR count: `{payload['baseline']['adr']['count']}`",
        f"- Test file count: `{payload['baseline']['tests']['count']}`",
        f"- Core docs present: `{payload['baseline']['docs']['present_count']}/{payload['baseline']['docs']['expected_count']}`",
        "",
    ]
    return "\n".join(lines) + "\n"


def write_readiness_artifacts(payload: dict[str, Any], root: Path = REPO_ROOT) -> tuple[Path, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    target_dir = root / "docs" / "_ops" / "final_readiness" / f"run_{stamp}"
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / "summary.json"
    md_path = target_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final readiness report from repo artifacts.")
    parser.parse_args()
    payload = build_readiness_payload(REPO_ROOT)
    json_path, md_path = write_readiness_artifacts(payload, REPO_ROOT)
    print(f"[OK] wrote readiness artifacts: {_rel_posix(json_path)} ; {_rel_posix(md_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

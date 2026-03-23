from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from tools.package_distribution import REPO_ROOT, build_distribution_payload

QUALITY_GATES_DIR = REPO_ROOT / "docs" / "_ops" / "quality_gates"
RELEASE_DIR = REPO_ROOT / "docs" / "_ops" / "release_artifacts"


def latest_successful_quality_gate_run(quality_gates_dir: Path = QUALITY_GATES_DIR) -> Path | None:
    if not quality_gates_dir.exists():
        return None
    candidates: list[Path] = []
    for path in quality_gates_dir.glob("run_*"):
        summary = path / "summary.json"
        if not summary.exists():
            continue
        try:
            payload = json.loads(summary.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("status") == "OK":
            candidates.append(path)
    if not candidates:
        return None
    return sorted(candidates)[-1]


def build_release_artifact_manifest(release_id: str, repo_root: Path = REPO_ROOT) -> dict:
    qg_run = latest_successful_quality_gate_run(repo_root / "docs" / "_ops" / "quality_gates")
    payload = build_distribution_payload(repo_root=repo_root)
    return {
        "release_id": release_id,
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "quality_gate_run": (
            str(qg_run.relative_to(repo_root)).replace("\\", "/")
            if qg_run is not None else ""
        ),
        "distribution": payload,
    }


def write_release_artifact_manifest(release_id: str, repo_root: Path = REPO_ROOT) -> Path:
    output_path = repo_root / "docs" / "_ops" / "release_artifacts" / f"{release_id}.json"
    payload = build_release_artifact_manifest(release_id=release_id, repo_root=repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a release artifact manifest.")
    parser.add_argument("--release-id", required=True, help="Logical release identifier.")
    args = parser.parse_args()
    write_release_artifact_manifest(release_id=args.release_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

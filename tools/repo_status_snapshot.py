from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rel_posix(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _run_git(args: list[str], root: Path) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.returncode, completed.stdout.strip()
    except OSError:
        return 127, ""


def build_repo_status_snapshot(root: Path = REPO_ROOT) -> dict[str, Any]:
    branch_rc, branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    sha_rc, sha = _run_git(["rev-parse", "--short", "HEAD"], root)
    status_rc, status = _run_git(["status", "--short"], root)

    quality_dir = root / "docs" / "_ops" / "quality_gates"
    quality_runs = sorted([path for path in quality_dir.glob("run_*") if path.is_dir()]) if quality_dir.exists() else []

    return {
        "generated_at": _iso_now(),
        "repo_root": root.as_posix(),
        "git": {
            "branch": branch if branch_rc == 0 else None,
            "commit_short": sha if sha_rc == 0 else None,
            "status_lines": [line for line in status.splitlines() if line] if status_rc == 0 else [],
        },
        "quality_gates": {
            "run_count": len(quality_runs),
            "latest_run_dir": _rel_posix(quality_runs[-1], root) if quality_runs else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact repository status snapshot.")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    payload = build_repo_status_snapshot(REPO_ROOT)
    output = args.output or (REPO_ROOT / "docs" / "_ops" / "status" / "repo_status_snapshot.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] wrote repo status snapshot: {output.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

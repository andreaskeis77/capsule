from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT_STR = str(REPO_ROOT)
if REPO_ROOT_STR not in sys.path:
    sys.path.insert(0, REPO_ROOT_STR)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def docs_dir(repo_root: Path) -> Path:
    return repo_root / "docs"


@pytest.fixture(scope="session")
def ops_dir(docs_dir: Path) -> Path:
    return docs_dir / "_ops"


@pytest.fixture(scope="session")
def quality_gates_dir(ops_dir: Path) -> Path:
    return ops_dir / "quality_gates"


@pytest.fixture
def tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    return root


@pytest.fixture
def write_json() -> Callable[[Path, dict[str, Any]], Path]:
    def _write_json(path: Path, payload: dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    return _write_json


@pytest.fixture
def make_quality_gate_run(tmp_repo_root: Path, write_json: Callable[[Path, dict[str, Any]], Path]):
    base = tmp_repo_root / "docs" / "_ops" / "quality_gates"

    def _make(run_name: str = "run_20260322-000000", *, status: str = "OK", failed_required_steps: list[str] | None = None) -> Path:
        run_dir = base / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_utc": "2026-03-22T00:00:00+00:00",
            "repo_root": str(tmp_repo_root),
            "base_url": "http://127.0.0.1:8765",
            "server_started": False,
            "steps": [],
            "failed_required_steps": failed_required_steps or [],
            "status": status,
        }
        write_json(run_dir / "summary.json", payload)
        (run_dir / "summary.md").write_text(f"# Quality Gates\n\n- Status: {status}\n", encoding="utf-8")
        return run_dir

    return _make

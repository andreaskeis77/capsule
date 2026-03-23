from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = REPO_ROOT / "docs" / "adr"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _posix(path: Path) -> str:
    return path.as_posix()


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def collect_top_level_contract(root: Path = REPO_ROOT) -> dict[str, bool]:
    expected = [
        "docs",
        "src",
        "tests",
        "tools",
        "ontology",
        "templates",
        "README.md",
        "pytest.ini",
        "requirements.txt",
        "pyproject.toml",
    ]
    return {entry: (root / entry).exists() for entry in expected}


def collect_adr_summary(root: Path = REPO_ROOT) -> dict[str, Any]:
    adr_dir = root / "docs" / "adr"
    adrs = sorted(
        path
        for path in adr_dir.glob("ADR-*.md")
        if path.name != "ADR-INDEX.md"
    )
    index_exists = (adr_dir / "ADR-INDEX.md").exists()
    latest = adrs[-1].name if adrs else None
    return {
        "count": len(adrs),
        "index_present": index_exists,
        "latest": latest,
    }


def collect_doc_summary(root: Path = REPO_ROOT) -> dict[str, Any]:
    docs = root / "docs"
    core = [
        "INDEX.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "RUNBOOK.md",
        "PROJECT_STATE.md",
        "HANDOFF_GUIDE.md",
        "DEVELOPER_WORKFLOW.md",
        "TEST_STRATEGY.md",
        "OBSERVABILITY.md",
        "SECURITY.md",
        "PACKAGING.md",
        "RELEASE_PROCESS.md",
        "RELEASE_ARTIFACTS.md",
    ]
    present = {name: (docs / name).exists() for name in core}
    return {
        "core_present": present,
        "present_count": sum(1 for value in present.values() if value),
        "expected_count": len(core),
    }


def collect_test_summary(root: Path = REPO_ROOT) -> dict[str, Any]:
    test_files = sorted((root / "tests").glob("test_*.py"))
    return {
        "count": len(test_files),
        "sample": [path.name for path in test_files[:10]],
    }


def build_baseline_payload(root: Path = REPO_ROOT) -> dict[str, Any]:
    return {
        "generated_at": _iso_now(),
        "repo_root": _posix(root),
        "repo_name": root.name,
        "top_level_contract": collect_top_level_contract(root),
        "adr": collect_adr_summary(root),
        "docs": collect_doc_summary(root),
        "tests": collect_test_summary(root),
    }


def write_baseline_report(
    payload: dict[str, Any],
    output_path: Path | None = None,
    root: Path = REPO_ROOT,
) -> Path:
    target = output_path or (root / "docs" / "_ops" / "baseline" / "final_repo_baseline.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final repository baseline payload.")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    payload = build_baseline_payload(REPO_ROOT)
    written = write_baseline_report(payload, args.output, REPO_ROOT)
    print(f"[OK] wrote baseline payload: {_safe_rel(written, REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

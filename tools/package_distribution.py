from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
MANIFEST_PATH = REPO_ROOT / "MANIFEST.in"


def load_pyproject(path: Path = PYPROJECT_PATH) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def package_metadata(pyproject: dict) -> dict:
    project = pyproject.get("project", {})
    return {
        "name": project.get("name", ""),
        "version": project.get("version", ""),
        "requires_python": project.get("requires-python", ""),
        "readme": project.get("readme", ""),
        "optional_dependency_groups": sorted(project.get("optional-dependencies", {}).keys()),
    }


def parse_manifest(path: Path = MANIFEST_PATH) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def package_file_inventory(repo_root: Path = REPO_ROOT) -> dict:
    docs = sorted(str(p.relative_to(repo_root)).replace("\\", "/") for p in (repo_root / "docs").glob("*.md"))
    workflows = sorted(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in (repo_root / ".github" / "workflows").glob("*.yml")
    )
    top_files = []
    for rel in ["README.md", "requirements.txt", "pytest.ini", ".env.example", "pyproject.toml", "MANIFEST.in"]:
        path = repo_root / rel
        if path.exists():
            top_files.append(rel)
    return {
        "top_level_files": top_files,
        "doc_markdown_files": docs,
        "workflow_files": workflows,
    }


def build_distribution_payload(repo_root: Path = REPO_ROOT) -> dict:
    pyproject = load_pyproject(repo_root / "pyproject.toml")
    manifest_lines = parse_manifest(repo_root / "MANIFEST.in")
    inventory = package_file_inventory(repo_root)
    return {
        "metadata": package_metadata(pyproject),
        "manifest_rule_count": len(manifest_lines),
        "inventory": inventory,
    }


def write_distribution_payload(output_path: Path, repo_root: Path = REPO_ROOT) -> Path:
    payload = build_distribution_payload(repo_root=repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit packaging/distribution metadata for the repo.")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs" / "_ops" / "packaging" / "distribution_payload.json"),
        help="Where to write the JSON payload.",
    )
    args = parser.parse_args()
    write_distribution_payload(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path


def test_pyproject_exists_and_defines_project():
    pyproject = Path("pyproject.toml")
    assert pyproject.exists()
    text = pyproject.read_text(encoding="utf-8")
    assert "[project]" in text
    assert 'name = "capsule-wardrobe-rag"' in text


def test_manifest_exists_and_includes_readme():
    manifest = Path("MANIFEST.in")
    assert manifest.exists()
    text = manifest.read_text(encoding="utf-8")
    assert "include README.md" in text


def test_package_workflow_exists():
    workflow = Path(".github") / "workflows" / "package-release.yml"
    assert workflow.exists()

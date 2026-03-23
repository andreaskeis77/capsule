from __future__ import annotations

import json

import tools.package_distribution as pkg


def test_parse_manifest_ignores_blank_and_comment_lines(tmp_path):
    manifest = tmp_path / "MANIFEST.in"
    manifest.write_text(
        "# comment\n\ninclude README.md\nrecursive-include docs *.md\n",
        encoding="utf-8",
    )

    lines = pkg.parse_manifest(manifest)

    assert lines == ["include README.md", "recursive-include docs *.md"]


def test_build_distribution_payload_collects_metadata_and_inventory(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "docs" / "PACKAGING.md").write_text("ok\n", encoding="utf-8")
    (tmp_path / ".github" / "workflows" / "package-release.yml").write_text("name: x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Capsule\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest==9.0.2\n", encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("DEBUG=0\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "capsule-wardrobe-rag"
version = "0.1.0"
requires-python = ">=3.12"
readme = "README.md"

[project.optional-dependencies]
dev = ["pytest==9.0.2"]
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "MANIFEST.in").write_text("include README.md\n", encoding="utf-8")

    payload = pkg.build_distribution_payload(repo_root=tmp_path)

    assert payload["metadata"]["name"] == "capsule-wardrobe-rag"
    assert payload["metadata"]["optional_dependency_groups"] == ["dev"]
    assert payload["manifest_rule_count"] == 1
    assert "README.md" in payload["inventory"]["top_level_files"]
    assert "docs/PACKAGING.md" in payload["inventory"]["doc_markdown_files"]


def test_write_distribution_payload_emits_json(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "README.md").write_text("# Capsule\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest==9.0.2\n", encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("DEBUG=0\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "capsule-wardrobe-rag"
version = "0.1.0"
requires-python = ">=3.12"
readme = "README.md"
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "MANIFEST.in").write_text("include README.md\n", encoding="utf-8")

    output = tmp_path / "docs" / "_ops" / "packaging" / "distribution_payload.json"
    pkg.write_distribution_payload(output_path=output, repo_root=tmp_path)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["metadata"]["version"] == "0.1.0"

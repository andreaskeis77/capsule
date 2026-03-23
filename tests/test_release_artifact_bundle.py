from __future__ import annotations

import json

import tools.release_artifact_bundle as rel


def test_latest_successful_quality_gate_run_prefers_latest_ok(tmp_path):
    qg = tmp_path / "docs" / "_ops" / "quality_gates"
    a = qg / "run_20260322-100000"
    b = qg / "run_20260322-100100"
    c = qg / "run_20260322-100200"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    c.mkdir(parents=True)
    (a / "summary.json").write_text(json.dumps({"status": "FAIL"}), encoding="utf-8")
    (b / "summary.json").write_text(json.dumps({"status": "OK"}), encoding="utf-8")
    (c / "summary.json").write_text(json.dumps({"status": "OK"}), encoding="utf-8")

    latest = rel.latest_successful_quality_gate_run(qg)

    assert latest == c


def test_build_release_artifact_manifest_uses_posix_relative_paths(tmp_path):
    (tmp_path / "docs" / "_ops" / "quality_gates" / "run_20260322-211309").mkdir(parents=True)
    summary = tmp_path / "docs" / "_ops" / "quality_gates" / "run_20260322-211309" / "summary.json"
    summary.write_text(json.dumps({"status": "OK"}), encoding="utf-8")

    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
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

    payload = rel.build_release_artifact_manifest("v1.0.0", repo_root=tmp_path)

    assert payload["release_id"] == "v1.0.0"
    assert payload["quality_gate_run"] == "docs/_ops/quality_gates/run_20260322-211309"

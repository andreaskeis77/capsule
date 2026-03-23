from __future__ import annotations

import json
from pathlib import Path

import tools.ops_report_index as idx


def test_build_index_collects_recent_quality_gate_and_release_entries(tmp_path, monkeypatch):
    repo = tmp_path
    qg = repo / "docs" / "_ops" / "quality_gates" / "run_20260322-100000"
    qg.mkdir(parents=True)
    (qg / "summary.json").write_text(json.dumps({"status": "OK", "generated_utc": "2026-03-22T10:00:00+00:00"}), encoding="utf-8")
    (qg / "diagnosis.json").write_text(json.dumps({"failure_count": 0}), encoding="utf-8")

    rel = repo / "docs" / "_ops" / "releases" / "v1_20260322"
    rel.mkdir(parents=True)
    (rel / "release_evidence.json").write_text(
        json.dumps({
            "release_id": "v1",
            "commit": "abc123",
            "quality_gate_status": "OK",
            "generated_at_utc": "2026-03-22T10:05:00+00:00",
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(idx, "REPO_ROOT", repo)
    monkeypatch.setattr(idx, "OPS_ROOT", repo / "docs" / "_ops")
    monkeypatch.setattr(idx, "QUALITY_GATES_DIR", repo / "docs" / "_ops" / "quality_gates")
    monkeypatch.setattr(idx, "RELEASES_DIR", repo / "docs" / "_ops" / "releases")
    monkeypatch.setattr(idx, "INDEX_DIR", repo / "docs" / "_ops" / "report_index")

    payload = idx.build_index(limit=5)
    assert payload["quality_gates"][0]["run_dir"] == "docs/_ops/quality_gates/run_20260322-100000"
    assert payload["releases"][0]["release_id"] == "v1"


def test_write_index_emits_markdown_and_json(tmp_path, monkeypatch):
    monkeypatch.setattr(idx, "INDEX_DIR", tmp_path / "docs" / "_ops" / "report_index")
    payload = {"generated_at_utc": "2026-03-22T10:00:00+00:00", "quality_gates": [], "releases": []}
    json_path, md_path = idx.write_index(payload)
    assert json_path.exists()
    assert md_path.exists()
    assert "Ops Report Index" in md_path.read_text(encoding="utf-8")

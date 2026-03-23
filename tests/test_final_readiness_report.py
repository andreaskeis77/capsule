from __future__ import annotations

import json

import tools.final_readiness_report as report


def test_build_readiness_payload_reads_latest_successful_run(tmp_path, monkeypatch):
    repo = tmp_path
    qg = repo / "docs" / "_ops" / "quality_gates"
    qg.mkdir(parents=True)
    bad = qg / "run_20260323-000000"
    good = qg / "run_20260323-010000"
    bad.mkdir()
    good.mkdir()
    (bad / "summary.json").write_text(json.dumps({"status": "FAIL"}), encoding="utf-8")
    (good / "summary.json").write_text(json.dumps({"status": "OK"}), encoding="utf-8")

    releases = repo / "docs" / "_ops" / "releases"
    releases.mkdir(parents=True)
    (releases / "release_v1.json").write_text(json.dumps({"release_id": "v1"}), encoding="utf-8")

    for name in ["docs", "src", "tests", "tools", "ontology", "templates"]:
        (repo / name).mkdir(parents=True, exist_ok=True)
    for name in ["README.md", "pytest.ini", "requirements.txt", "pyproject.toml"]:
        (repo / name).write_text("", encoding="utf-8")
    adr = repo / "docs" / "adr"
    adr.mkdir(parents=True, exist_ok=True)
    (adr / "ADR-0018-test.md").write_text("# ADR\n", encoding="utf-8")
    (repo / "tests" / "test_alpha.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    payload = report.build_readiness_payload(repo)

    assert payload["quality_gates"]["status"] == "OK"
    assert payload["quality_gates"]["latest_successful_run_dir"] == "docs/_ops/quality_gates/run_20260323-010000"
    assert payload["release_evidence"]["present"] is True
    assert payload["readiness"]["quality_gate_ready"] is True
    assert payload["readiness"]["overall_ready"] is True


def test_write_readiness_artifacts_creates_json_and_markdown(tmp_path):
    payload = {
        "generated_at": "2026-03-23T00:00:00+00:00",
        "baseline": {"adr": {"count": 1}, "tests": {"count": 2}, "docs": {"present_count": 3, "expected_count": 4}},
        "quality_gates": {"status": "OK", "latest_successful_run_dir": "docs/_ops/quality_gates/run_x"},
        "release_evidence": {"present": False, "latest_file": None, "release_id": None},
        "readiness": {
            "structure_ready": True,
            "documentation_ready": True,
            "quality_gate_ready": True,
            "release_evidence_present": False,
            "overall_ready": True,
        },
    }

    json_path, md_path = report.write_readiness_artifacts(payload, tmp_path)

    assert json_path.exists()
    assert md_path.exists()
    assert "Final Readiness Report" in md_path.read_text(encoding="utf-8")

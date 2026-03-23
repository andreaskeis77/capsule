from __future__ import annotations

import json
from pathlib import Path

import tools.quality_gate_diagnose as diag


def test_build_diagnosis_classifies_pytest_assertion_failure(tmp_path):
    run_dir = tmp_path / "docs" / "_ops" / "quality_gates" / "run_1"
    run_dir.mkdir(parents=True)
    log_rel = Path("docs/_ops/quality_gates/run_1/step_pytest.log")
    (tmp_path / log_rel).write_text("AssertionError\nFAILED tests/test_x.py\n", encoding="utf-8")
    summary = {
        "generated_utc": "2026-03-22T00:00:00+00:00",
        "steps": [
            {
                "name": "pytest",
                "returncode": 1,
                "log_file": str(log_rel).replace("\\", "/"),
            }
        ],
    }

    diagnosis = diag.build_diagnosis(summary, repo_root=tmp_path)
    assert diagnosis["status"] == "FAIL"
    assert diagnosis["failure_count"] == 1
    assert diagnosis["failures"][0]["category"] == "test_assertion"


def test_write_diagnosis_writes_json_and_markdown(tmp_path):
    run_dir = tmp_path / "run_2"
    run_dir.mkdir(parents=True)
    payload = {
        "generated_at_utc": "2026-03-22T00:00:00+00:00",
        "status": "OK",
        "failed_steps": [],
        "failure_count": 0,
        "failures": [],
    }
    json_path, md_path = diag.write_diagnosis(run_dir, payload)
    assert json.loads(json_path.read_text(encoding="utf-8"))["status"] == "OK"
    assert "All required steps passed" in md_path.read_text(encoding="utf-8")

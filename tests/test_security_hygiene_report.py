from __future__ import annotations

import json
from pathlib import Path

from tools import security_hygiene_report as report


def test_build_security_hygiene_payload_reads_latest_ok_run(tmp_path):
    repo_root = tmp_path
    (repo_root / "docs" / "_ops" / "quality_gates" / "run_1").mkdir(parents=True)
    (repo_root / "docs" / "_ops" / "quality_gates" / "run_2").mkdir(parents=True)
    (repo_root / "docs" / "_ops" / "quality_gates" / "run_1" / "summary.json").write_text(
        json.dumps({"status": "FAIL"}), encoding="utf-8"
    )
    (repo_root / "docs" / "_ops" / "quality_gates" / "run_2" / "summary.json").write_text(
        json.dumps({"status": "OK"}), encoding="utf-8"
    )
    (repo_root / "requirements.txt").write_text("fastapi==0.1.0\n", encoding="utf-8")
    (repo_root / ".env.example").write_text("WARDROBE_ENV=dev\n", encoding="utf-8")
    (repo_root / "tools").mkdir()
    (repo_root / "tools" / "secret_scan.py").write_text("print('ok')\n", encoding="utf-8")
    (repo_root / ".github" / "workflows").mkdir(parents=True)
    (repo_root / ".github" / "workflows" / "quality-gates.yml").write_text("name: qg\n", encoding="utf-8")

    payload = report.build_security_hygiene_payload(repo_root)

    assert payload["status"] == "OK"
    assert payload["latest_quality_gates"]["run_name"] == "run_2"
    assert payload["warnings"] == []


def test_render_markdown_includes_warning_section():
    payload = {
        "generated_at": "2026-03-22T00:00:00Z",
        "status": "WARN",
        "warnings": ["No successful quality gate run was found."],
        "inventory": {
            "required_controls_present": False,
            "optional_controls_present": 0,
            "optional_controls_total": 2,
            "requirements": {"pinned": 1, "total": 2},
        },
        "latest_quality_gates": None,
        "latest_release_evidence": None,
    }

    rendered = report.render_markdown(payload)

    assert "# Security Hygiene Report" in rendered
    assert "## Warnings" in rendered
    assert "No successful quality gate run was found." in rendered

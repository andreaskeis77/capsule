from __future__ import annotations

import json
from pathlib import Path

from tools.ci_artifact_summary import _find_latest_run, _render_summary


def test_find_latest_run_picks_highest_sorted_name(tmp_path: Path):
    (tmp_path / "run_20260322-090000").mkdir()
    latest = tmp_path / "run_20260322-120000"
    latest.mkdir()
    assert _find_latest_run(tmp_path) == latest


def test_render_summary_includes_steps_and_result(tmp_path: Path):
    run_dir = tmp_path / "run_20260322-120000"
    run_dir.mkdir()
    payload = {
        "result": "OK",
        "base_url": "http://127.0.0.1:5012",
        "steps": [
            {
                "name": "pytest",
                "status": "ok",
                "return_code": 0,
                "duration_s": 6.125,
                "log_file": "docs/_ops/quality_gates/run_x/step_pytest.log",
            }
        ],
    }

    rendered = _render_summary(payload, run_dir)
    assert "# CI Quality Gates Summary" in rendered
    assert "Result: **OK**" in rendered
    assert "| pytest | ok | 0 | 6.125 |" in rendered
    assert "All required quality gates passed." in rendered

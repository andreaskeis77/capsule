from __future__ import annotations

import json
from pathlib import Path

import tools.test_suite_report as report


def test_build_suite_report_counts_tests_and_markers(tmp_path):
    repo_root = tmp_path / "repo"
    tests_dir = repo_root / "tests"
    tests_dir.mkdir(parents=True)

    (tests_dir / "test_alpha.py").write_text(
        "import pytest\n\n@pytest.mark.smoke\ndef test_alpha():\n    assert True\n",
        encoding="utf-8",
    )
    (tests_dir / "test_beta.py").write_text(
        "import pytest\n\n@pytest.mark.contract\n@pytest.mark.ops\ndef test_beta_one():\n    assert True\n\ndef test_beta_two():\n    assert True\n",
        encoding="utf-8",
    )

    payload = report.build_suite_report(tests_dir=tests_dir, repo_root=repo_root)

    assert payload["tests_dir"] == "tests"
    assert payload["total_files"] == 2
    assert payload["total_test_functions"] == 3
    assert payload["marker_usage"]["smoke"] == 1
    assert payload["marker_usage"]["contract"] == 1
    assert payload["marker_usage"]["ops"] == 1


def test_write_report_emits_json_and_markdown(tmp_path):
    out_dir = tmp_path / "docs" / "_ops" / "test_suite"
    payload = {
        "generated_utc": "2026-03-22T00:00:00+00:00",
        "tests_dir": "tests",
        "total_files": 1,
        "total_test_functions": 2,
        "marker_usage": {"smoke": 1},
        "files": [{"path": "tests/test_alpha.py", "test_functions": 2, "markers": ["smoke"]}],
    }
    report.write_report(out_dir, payload)
    assert json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))["total_files"] == 1
    assert "# Test Suite Report" in (out_dir / "summary.md").read_text(encoding="utf-8")

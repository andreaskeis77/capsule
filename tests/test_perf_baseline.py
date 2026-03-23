from __future__ import annotations

import json
from pathlib import Path

import tools.perf_baseline as perf


def test_normalize_metric_name_cleans_common_separators():
    assert perf.normalize_metric_name("API Main / import time") == "api_main_import_time"


def test_summarize_durations_computes_expected_fields():
    summary = perf.summarize_durations([11.0, 9.0, 10.0])
    assert summary == {
        "runs": 3.0,
        "min_ms": 9.0,
        "median_ms": 10.0,
        "mean_ms": 10.0,
        "max_ms": 11.0,
    }


def test_build_and_write_baseline_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(perf, "utc_timestamp", lambda: "20260322-220000")
    payload = perf.build_baseline_payload(
        suite_id="Import Hotpaths",
        metrics={"api main": {"runs": 1.0, "median_ms": 12.3, "mean_ms": 12.3, "min_ms": 12.3, "max_ms": 12.3}},
        metadata={"commit": "abc123"},
        created_at="2026-03-22T22:00:00+00:00",
    )
    run_dir = perf.write_baseline_artifacts(payload, perf_dir=tmp_path)
    assert run_dir == tmp_path / "run_20260322-220000_import_hotpaths"
    summary_json = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary_json["suite_id"] == "import_hotpaths"
    summary_md = (run_dir / "summary.md").read_text(encoding="utf-8")
    assert "# Performance baseline: import_hotpaths" in summary_md
    assert "api_main" in summary_md

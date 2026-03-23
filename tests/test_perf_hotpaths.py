from __future__ import annotations

import tools.perf_hotpaths as hotpaths


def test_build_import_metrics_creates_single_run_summaries():
    metrics = hotpaths.build_import_metrics([
        {"module": "src.api_main", "elapsed_ms": 12.5},
        {"module": "src.api_v2", "elapsed_ms": 7.0},
    ])
    assert metrics["import_src_api_main"]["median_ms"] == 12.5
    assert metrics["import_src_api_v2"]["runs"] == 1.0

from __future__ import annotations

import tools.perf_compare as perf_compare


def _payload(name: str, median_ms: float) -> dict:
    return {
        "suite_id": name,
        "metrics": {
            "import_api_main": {
                "median_ms": median_ms,
                "mean_ms": median_ms,
                "min_ms": median_ms,
                "max_ms": median_ms,
                "runs": 1.0,
            }
        },
    }


def test_compare_payloads_flags_regression_over_tolerance():
    report = perf_compare.compare_payloads(_payload("base", 10.0), _payload("cand", 13.0), tolerance_pct=20.0)
    assert report["status"] == "FAIL"
    assert report["regressions"][0]["metric"] == "import_api_main"


def test_compare_payloads_reports_improvement():
    report = perf_compare.compare_payloads(_payload("base", 10.0), _payload("cand", 8.0), tolerance_pct=10.0)
    assert report["status"] == "OK"
    assert report["improvements"][0]["delta_pct"] == -20.0

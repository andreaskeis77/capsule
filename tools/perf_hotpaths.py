from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

from tools.perf_baseline import build_baseline_payload, write_baseline_artifacts

DEFAULT_IMPORT_TARGETS = [
    "src.api_main",
    "src.api_v2",
    "src.ontology_runtime",
    "src.run_registry",
]


def measure_import_time(module_name: str) -> dict[str, Any]:
    started = time.perf_counter()
    module = importlib.import_module(module_name)
    finished = time.perf_counter()
    return {
        "module": module.__name__,
        "elapsed_ms": round((finished - started) * 1000.0, 3),
    }


def build_import_metrics(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for result in results:
        key = f"import_{result['module'].replace('.', '_')}"
        elapsed_ms = float(result["elapsed_ms"])
        metrics[key] = {
            "runs": 1.0,
            "min_ms": elapsed_ms,
            "median_ms": elapsed_ms,
            "mean_ms": elapsed_ms,
            "max_ms": elapsed_ms,
            "durations_ms": [elapsed_ms],
        }
    return metrics


def build_hotpath_payload(targets: list[str], *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    results = [measure_import_time(target) for target in targets]
    payload = build_baseline_payload(
        suite_id="import_hotpaths",
        metrics=build_import_metrics(results),
        metadata={"targets": targets, **(metadata or {})},
    )
    payload["results"] = results
    return payload


def main(argv: list[str] | None = None) -> int:
    targets = list(argv or DEFAULT_IMPORT_TARGETS)
    payload = build_hotpath_payload(targets, metadata={"cwd": str(Path.cwd())})
    run_dir = write_baseline_artifacts(payload)
    (run_dir / "results.json").write_text(json.dumps(payload["results"], indent=2), encoding="utf-8")
    print(f"[OK] wrote hot-path baseline: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

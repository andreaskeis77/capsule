from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PERF_BASELINES_DIR = REPO_ROOT / "docs" / "_ops" / "performance" / "baselines"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def normalize_metric_name(name: str) -> str:
    cleaned = []
    for ch in name.strip().lower():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in {"-", "_", ".", " ", "/"}:
            cleaned.append("_")
    normalized = "".join(cleaned)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def summarize_durations(durations_ms: Iterable[float]) -> dict[str, float]:
    values = [float(v) for v in durations_ms]
    if not values:
        raise ValueError("durations_ms must not be empty")
    ordered = sorted(values)
    return {
        "runs": float(len(ordered)),
        "min_ms": round(ordered[0], 3),
        "median_ms": round(statistics.median(ordered), 3),
        "mean_ms": round(statistics.fmean(ordered), 3),
        "max_ms": round(ordered[-1], 3),
    }


def measure_callable(fn: Callable[[], Any], *, repeat: int = 7, warmups: int = 1) -> dict[str, Any]:
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    if warmups < 0:
        raise ValueError("warmups must be >= 0")

    for _ in range(warmups):
        fn()

    durations_ms: list[float] = []
    for _ in range(repeat):
        started = time.perf_counter()
        fn()
        finished = time.perf_counter()
        durations_ms.append((finished - started) * 1000.0)

    summary = summarize_durations(durations_ms)
    summary["durations_ms"] = [round(v, 3) for v in durations_ms]
    return summary


def build_baseline_payload(
    *,
    suite_id: str,
    metrics: dict[str, dict[str, Any]],
    metadata: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    if not metrics:
        raise ValueError("metrics must not be empty")

    normalized_metrics: dict[str, dict[str, Any]] = {}
    for metric_name, metric in metrics.items():
        key = normalize_metric_name(metric_name)
        if not key:
            raise ValueError(f"invalid metric name: {metric_name!r}")
        normalized_metrics[key] = dict(metric)

    return {
        "suite_id": normalize_metric_name(suite_id),
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "metadata": dict(metadata or {}),
        "metrics": normalized_metrics,
    }


def render_markdown_summary(payload: dict[str, Any]) -> str:
    lines = [
        f"# Performance baseline: {payload['suite_id']}",
        "",
        f"- created_at: {payload['created_at']}",
        f"- python: {payload['python']}",
    ]
    if payload.get("metadata"):
        lines.append(f"- metadata: {json.dumps(payload['metadata'], sort_keys=True)}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| metric | median_ms | mean_ms | min_ms | max_ms | runs |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for metric_name, metric in sorted(payload["metrics"].items()):
        lines.append(
            "| {name} | {median_ms} | {mean_ms} | {min_ms} | {max_ms} | {runs} |".format(
                name=metric_name,
                median_ms=metric.get("median_ms", ""),
                mean_ms=metric.get("mean_ms", ""),
                min_ms=metric.get("min_ms", ""),
                max_ms=metric.get("max_ms", ""),
                runs=metric.get("runs", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_baseline_artifacts(payload: dict[str, Any], *, perf_dir: Path = PERF_BASELINES_DIR) -> Path:
    run_dir = perf_dir / f"run_{utc_timestamp()}_{payload['suite_id']}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (run_dir / "summary.md").write_text(render_markdown_summary(payload), encoding="utf-8")
    return run_dir


def _parse_metric_args(metric_args: list[str]) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for metric_arg in metric_args:
        try:
            name, value = metric_arg.split("=", 1)
        except ValueError as exc:
            raise ValueError(f"invalid --metric value: {metric_arg!r}") from exc
        durations = [float(part) for part in value.split(",") if part.strip()]
        metrics[name] = summarize_durations(durations)
    return metrics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create performance baseline artifacts.")
    parser.add_argument("--suite-id", required=True)
    parser.add_argument(
        "--metric",
        action="append",
        default=[],
        help="Metric in the form name=12.1,11.9,12.0",
    )
    parser.add_argument("--metadata", action="append", default=[])
    args = parser.parse_args(argv)

    metadata: dict[str, Any] = {}
    for item in args.metadata:
        key, value = item.split("=", 1)
        metadata[key] = value

    metrics = _parse_metric_args(args.metric)
    payload = build_baseline_payload(suite_id=args.suite_id, metrics=metrics, metadata=metadata)
    run_dir = write_baseline_artifacts(payload)
    print(f"[OK] wrote performance baseline: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

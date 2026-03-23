from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare_payloads(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    tolerance_pct: float = 10.0,
) -> dict[str, Any]:
    baseline_metrics = baseline.get("metrics", {})
    candidate_metrics = candidate.get("metrics", {})

    regressions: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    missing_metrics: list[str] = []

    for name, base_metric in sorted(baseline_metrics.items()):
        cand_metric = candidate_metrics.get(name)
        if cand_metric is None:
            missing_metrics.append(name)
            continue
        base_median = float(base_metric["median_ms"])
        cand_median = float(cand_metric["median_ms"])
        delta_ms = round(cand_median - base_median, 3)
        delta_pct = round((delta_ms / base_median) * 100.0, 3) if base_median else 0.0
        record = {
            "metric": name,
            "baseline_median_ms": base_median,
            "candidate_median_ms": cand_median,
            "delta_ms": delta_ms,
            "delta_pct": delta_pct,
        }
        if delta_pct > tolerance_pct:
            regressions.append(record)
        elif delta_pct < -tolerance_pct:
            improvements.append(record)
        else:
            unchanged.append(record)

    status = "OK" if not regressions and not missing_metrics else "FAIL"
    return {
        "status": status,
        "tolerance_pct": tolerance_pct,
        "baseline_suite_id": baseline.get("suite_id"),
        "candidate_suite_id": candidate.get("suite_id"),
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
        "missing_metrics": missing_metrics,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Performance comparison",
        "",
        f"- status: {report['status']}",
        f"- tolerance_pct: {report['tolerance_pct']}",
        f"- baseline_suite_id: {report['baseline_suite_id']}",
        f"- candidate_suite_id: {report['candidate_suite_id']}",
        "",
    ]
    for section in ("regressions", "improvements", "unchanged"):
        lines.append(f"## {section}")
        lines.append("")
        items = report[section]
        if not items:
            lines.append("- none")
            lines.append("")
            continue
        lines.append("| metric | baseline_median_ms | candidate_median_ms | delta_ms | delta_pct |")
        lines.append("|---|---:|---:|---:|---:|")
        for item in items:
            lines.append(
                f"| {item['metric']} | {item['baseline_median_ms']} | {item['candidate_median_ms']} | {item['delta_ms']} | {item['delta_pct']} |"
            )
        lines.append("")
    if report["missing_metrics"]:
        lines.append("## missing_metrics")
        lines.append("")
        for metric in report["missing_metrics"]:
            lines.append(f"- {metric}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two performance baseline payloads.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--tolerance-pct", type=float, default=10.0)
    parser.add_argument("--write-markdown")
    args = parser.parse_args(argv)

    report = compare_payloads(
        _load_payload(args.baseline),
        _load_payload(args.candidate),
        tolerance_pct=args.tolerance_pct,
    )
    if args.write_markdown:
        Path(args.write_markdown).write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

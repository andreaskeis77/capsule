#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Any, Dict

try:
    from tools.ops_common import truncate_text
    from tools.ops_paths import bootstrap_repo_root
    from tools.reporting_common import render_table
except Exception:  # pragma: no cover - direct script execution fallback
    from ops_common import truncate_text  # type: ignore
    from ops_paths import bootstrap_repo_root  # type: ignore
    from reporting_common import render_table  # type: ignore

bootstrap_repo_root(__file__)

from src import settings
from src.run_registry import compute_kpis, list_events, list_runs


def _fmt(value: Any, max_len: int = 90) -> str:
    return truncate_text("" if value is None else str(value), max_len)


def _build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    settings.reload_settings()
    kpis = compute_kpis(since_hours=args.since_hours, component=args.component)
    runs = list_runs(
        limit=args.limit,
        offset=args.offset,
        component=args.component,
        status=args.status,
        op=args.op,
        since_hours=args.since_hours,
    )
    out: Dict[str, Any] = {"kpis": kpis, "runs": runs}
    if args.events > 0:
        out["events"] = {r["run_id"]: list_events(r["run_id"], limit=args.events) for r in runs}
    return out


def _render_markdown(payload: Dict[str, Any]) -> str:
    kpis = payload["kpis"]
    runs = payload["runs"]
    lines = [
        "# Run Registry Report",
        "",
        f"- DB: `{settings.DB_PATH}`",
        f"- Window since_hours: `{kpis.get('window_since_hours')}`",
        f"- Component: `{kpis.get('component')}`",
        f"- Total runs: `{kpis['total_runs']}`",
        f"- Counts: `{kpis['counts']}`",
        f"- RSR (success): `{kpis['RSR']}`",
        f"- PRR (partial): `{kpis['PRR']}`",
        f"- FRR (failed): `{kpis['FRR']}`",
        f"- MTTR_dev_minutes_avg: `{kpis['MTTR_dev_minutes_avg']}`",
        f"- Latest success started_at: `{kpis['latest_success_started_at']}`",
        "",
        "## Runs",
        "",
    ]
    lines.extend(
        render_table(
            ["started_at", "status", "dur_ms", "component", "op", "error_class", "run_id", "summary"],
            [
                [
                    _fmt(run.get("started_at"), 19),
                    _fmt(run.get("status"), 8),
                    _fmt(run.get("duration_ms"), 6),
                    _fmt(run.get("component"), 12),
                    _fmt(run.get("op"), 18),
                    _fmt(run.get("error_class"), 9),
                    _fmt(run.get("run_id"), 8),
                    _fmt(run.get("summary"), 80),
                ]
                for run in runs
            ],
        )
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Wardrobe Studio - Run Registry report")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--component", type=str, default=None)
    ap.add_argument("--status", type=str, default=None)
    ap.add_argument("--op", type=str, default=None)
    ap.add_argument("--since-hours", type=int, default=None)
    ap.add_argument("--events", type=int, default=0, help="Show up to N events per run")
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    ap.add_argument("--markdown", action="store_true", help="Output as Markdown")
    args = ap.parse_args()

    payload = _build_payload(args)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.markdown:
        print(_render_markdown(payload), end="")
        return 0

    kpis = payload["kpis"]
    runs = payload["runs"]
    print("=== Run Registry KPIs ===")
    print(f"DB: {settings.DB_PATH}")
    print(f"Window since_hours: {kpis.get('window_since_hours')}")
    print(f"Component: {kpis.get('component')}")
    print(f"Total runs: {kpis['total_runs']}")
    print(f"Counts: {kpis['counts']}")
    print(f"RSR (success): {kpis['RSR']}")
    print(f"PRR (partial): {kpis['PRR']}")
    print(f"FRR (failed): {kpis['FRR']}")
    print(f"MTTR_dev_minutes_avg: {kpis['MTTR_dev_minutes_avg']}")
    print(f"Latest success started_at: {kpis['latest_success_started_at']}")
    print()

    print("=== Runs ===")
    print("started_at | status | dur_ms | component | op | error_class | run_id | summary")
    for run in runs:
        print(
            f"{_fmt(run.get('started_at'), 19)} | "
            f"{_fmt(run.get('status'), 8)} | "
            f"{_fmt(run.get('duration_ms'), 6)} | "
            f"{_fmt(run.get('component'), 12)} | "
            f"{_fmt(run.get('op'), 18)} | "
            f"{_fmt(run.get('error_class'), 9)} | "
            f"{_fmt(run.get('run_id'), 8)} | "
            f"{_fmt(run.get('summary'), 80)}"
        )
        if args.events > 0:
            for event in payload.get("events", {}).get(run["run_id"], []):
                print(f"    - {event.get('ts')} {event.get('level')} {event.get('event')}: {_fmt(event.get('message'), 120)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

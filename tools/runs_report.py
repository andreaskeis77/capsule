#!/usr/bin/env python3
# FILE: tools/runs_report.py
from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from src import settings
from src.run_registry import compute_kpis, list_events, list_runs


def _fmt(s: Any, max_len: int = 90) -> str:
    if s is None:
        return ""
    t = str(s)
    if len(t) > max_len:
        return t[: max_len - 3] + "..."
    return t


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
    args = ap.parse_args()

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

    if args.json:
        out: Dict[str, Any] = {"kpis": kpis, "runs": runs}
        if args.events > 0:
            out["events"] = {r["run_id"]: list_events(r["run_id"], limit=args.events) for r in runs}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

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
    for r in runs:
        print(
            f"{_fmt(r.get('started_at'), 19)} | "
            f"{_fmt(r.get('status'), 8)} | "
            f"{_fmt(r.get('duration_ms'), 6)} | "
            f"{_fmt(r.get('component'), 12)} | "
            f"{_fmt(r.get('op'), 18)} | "
            f"{_fmt(r.get('error_class'), 9)} | "
            f"{_fmt(r.get('run_id'), 8)} | "
            f"{_fmt(r.get('summary'), 80)}"
        )

        if args.events > 0:
            ev = list_events(r["run_id"], limit=args.events)
            for e in ev:
                print(f"    - {e.get('ts')} {e.get('level')} {e.get('event')}: {_fmt(e.get('message'), 120)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
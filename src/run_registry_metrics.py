from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def compute_kpis_from_runs(
    runs: List[Dict[str, Any]],
    *,
    since_hours: Optional[int] = None,
    component: Optional[str] = None,
) -> Dict[str, Any]:
    total = len(runs)
    counts = {"ok": 0, "failed": 0, "partial": 0, "started": 0}

    for run in runs:
        status = str(run.get("status") or "").lower()
        if status in counts:
            counts[status] += 1
        else:
            counts.setdefault(status, 0)
            counts[status] += 1

    def rate(value: int) -> Optional[float]:
        return (value / total) if total else None

    ordered = sorted(runs, key=lambda row: str(row.get("started_at") or ""))
    mttr_minutes: List[float] = []
    ok_starts: List[datetime] = []

    for run in ordered:
        if str(run.get("status") or "").lower() == "ok":
            ts = parse_timestamp(run.get("started_at"))
            if ts is not None:
                ok_starts.append(ts)

    for run in ordered:
        if str(run.get("status") or "").lower() != "failed":
            continue

        fail_finished = parse_timestamp(run.get("finished_at")) or parse_timestamp(run.get("started_at"))
        if fail_finished is None:
            continue

        next_ok = next((ts for ts in ok_starts if ts > fail_finished), None)
        if next_ok is not None:
            mttr_minutes.append((next_ok - fail_finished).total_seconds() / 60.0)

    latest_ok = next((run for run in runs if str(run.get("status") or "").lower() == "ok"), None)
    latest_ok_at = latest_ok.get("started_at") if latest_ok else None

    return {
        "total_runs": total,
        "counts": counts,
        "RSR": rate(counts.get("ok", 0)),
        "PRR": rate(counts.get("partial", 0)),
        "FRR": rate(counts.get("failed", 0)),
        "MTTR_dev_minutes_avg": (sum(mttr_minutes) / len(mttr_minutes)) if mttr_minutes else None,
        "latest_success_started_at": latest_ok_at,
        "window_since_hours": since_hours,
        "component": component,
    }

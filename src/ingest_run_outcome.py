from __future__ import annotations

from typing import Any, Dict, Tuple


def summarize_ingest_stats(stats: Any, *, dry_run: bool, fake_ai: bool, dur_ms: int) -> str:
    return (
        f"scanned={getattr(stats, 'scanned', 0)} processed={getattr(stats, 'processed', 0)} "
        f"ok={getattr(stats, 'ok', 0)} failed={getattr(stats, 'failed', 0)} "
        f"skipped={getattr(stats, 'skipped', 0)} quarantined={getattr(stats, 'quarantined', 0)} "
        f"dry_run={dry_run} fake_ai={fake_ai} dur_ms={dur_ms}"
    )


def decide_ingest_outcome(stats: Any) -> Tuple[str, int]:
    failed = int(getattr(stats, "failed", 0) or 0)
    ok = int(getattr(stats, "ok", 0) or 0)

    if failed > 0 and ok > 0:
        return "partial", 2
    if failed > 0 and ok == 0:
        return "failed", 2
    return "ok", 0


def _stats_payload(stats: Any) -> Dict[str, Any]:
    payload = getattr(stats, "__dict__", None)
    if isinstance(payload, dict):
        return dict(payload)
    return {
        "scanned": getattr(stats, "scanned", 0),
        "processed": getattr(stats, "processed", 0),
        "ok": getattr(stats, "ok", 0),
        "failed": getattr(stats, "failed", 0),
        "skipped": getattr(stats, "skipped", 0),
        "quarantined": getattr(stats, "quarantined", 0),
    }


def finalize_ingest_run(run: Any, stats: Any, *, dry_run: bool, fake_ai: bool, dur_ms: int) -> int:
    summary = summarize_ingest_stats(stats, dry_run=dry_run, fake_ai=fake_ai, dur_ms=dur_ms)
    outcome, exit_code = decide_ingest_outcome(stats)

    run.event(
        "ingest.done",
        data={
            "stats": _stats_payload(stats),
            "dur_ms": dur_ms,
            "decision": outcome,
        },
    )

    if outcome == "partial":
        run.partial(summary=summary)
        return exit_code
    if outcome == "failed":
        run.fail(summary=summary)
        return exit_code

    run.ok(summary=summary)
    return exit_code

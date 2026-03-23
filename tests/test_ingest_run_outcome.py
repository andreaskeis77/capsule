from __future__ import annotations

from src.ingest_item_runner import Stats
from src.ingest_run_outcome import decide_ingest_outcome, finalize_ingest_run, summarize_ingest_stats


class FakeRun:
    def __init__(self):
        self.events = []
        self.status = None
        self.summary = None

    def event(self, name, level=None, message=None, data=None):
        self.events.append({"name": name, "level": level, "message": message, "data": data})

    def ok(self, summary=None):
        self.status = "ok"
        self.summary = summary

    def fail(self, summary=None):
        self.status = "failed"
        self.summary = summary

    def partial(self, summary=None):
        self.status = "partial"
        self.summary = summary


def test_decide_ingest_outcome_for_partial_run():
    outcome, exit_code = decide_ingest_outcome(Stats(ok=2, failed=1))
    assert outcome == "partial"
    assert exit_code == 2


def test_finalize_ingest_run_marks_ok_and_emits_done_event():
    run = FakeRun()
    stats = Stats(scanned=1, processed=1, ok=1, failed=0, skipped=0, quarantined=0)

    rc = finalize_ingest_run(run, stats, dry_run=False, fake_ai=True, dur_ms=125)

    assert rc == 0
    assert run.status == "ok"
    assert "dur_ms=125" in (run.summary or "")
    assert any(event["name"] == "ingest.done" for event in run.events)


def test_summarize_ingest_stats_contains_core_counters():
    summary = summarize_ingest_stats(Stats(scanned=3, processed=2, ok=1, failed=1, skipped=1, quarantined=1), dry_run=False, fake_ai=False, dur_ms=500)
    assert "scanned=3" in summary
    assert "processed=2" in summary
    assert "ok=1" in summary
    assert "failed=1" in summary
    assert "quarantined=1" in summary

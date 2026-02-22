# FILE: tests/test_run_registry.py
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src import settings
from src.db_schema import ensure_schema
from src.run_registry import run_context


def _get_run(db_path: Path, run_id: str):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    return row


def _get_events(db_path: Path, run_id: str):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM run_events WHERE run_id = ? ORDER BY id", (run_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def test_run_registry_ok(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()
    ensure_schema()

    with run_context("test", "ok_run", meta={"a": 1}) as r:
        r.event("step.start", "hello", data={"x": 1})
        r.event("step.end", "bye", data={"y": 2})

    row = _get_run(db_path, r.run_id)
    assert row is not None
    assert row["status"] == "ok"
    assert row["duration_ms"] is not None
    assert row["component"] == "test"
    assert row["op"] == "ok_run"

    events = _get_events(db_path, r.run_id)
    assert len(events) == 2
    assert events[0]["event"] == "step.start"
    assert events[1]["event"] == "step.end"


def test_run_registry_fail(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()
    ensure_schema()

    with pytest.raises(RuntimeError):
        with run_context("test", "fail_run") as r:
            r.event("before", "will fail")
            raise RuntimeError("boom")

    row = _get_run(db_path, r.run_id)
    assert row is not None
    assert row["status"] == "failed"
    assert row["error_class"] == "permanent"
    assert "RuntimeError" in (row["summary"] or "")
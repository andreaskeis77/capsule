# FILE: src/run_registry.py
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional

from src import settings
from src.db_schema import ensure_schema


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception:
        pass
    return conn


def _safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        return json.dumps({"_unserializable": str(obj)}, ensure_ascii=False, separators=(",", ":"))


@dataclass
class RunHandle:
    run_id: str
    component: str
    op: str
    _t0: float

    def event(self, event: str, message: str | None = None, *, level: str = "INFO", data: Any = None) -> None:
        log_event(self.run_id, level=level, event=event, message=message, data=data)

    def ok(self, summary: str | None = None) -> None:
        finish_run(self.run_id, status="ok", error_class=None, duration_ms=self._duration_ms(), summary=summary)

    def fail(self, *, error_class: str = "permanent", summary: str | None = None) -> None:
        finish_run(self.run_id, status="failed", error_class=error_class, duration_ms=self._duration_ms(), summary=summary)

    def partial(self, summary: str | None = None) -> None:
        finish_run(self.run_id, status="partial", error_class="permanent", duration_ms=self._duration_ms(), summary=summary)

    def _duration_ms(self) -> int:
        return int((time.perf_counter() - self._t0) * 1000)


def start_run(component: str, op: str, *, meta: Optional[Dict[str, Any]] = None) -> RunHandle:
    ensure_schema()  # ensures run tables exist too

    run_id = str(uuid.uuid4())
    t0 = time.perf_counter()

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO runs (run_id, component, op, status, meta_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, component, op, "started", _safe_json(meta or {})),
        )
        conn.commit()
    finally:
        conn.close()

    return RunHandle(run_id=run_id, component=component, op=op, _t0=t0)


def log_event(run_id: str, *, level: str, event: str, message: str | None = None, data: Any = None) -> None:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO run_events (run_id, level, event, message, data_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, level.upper(), event, message, _safe_json(data) if data is not None else None),
        )
        conn.commit()
    finally:
        conn.close()


def finish_run(
    run_id: str,
    *,
    status: str,
    error_class: str | None,
    duration_ms: int | None,
    summary: str | None,
) -> None:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE runs
            SET status = ?,
                error_class = ?,
                finished_at = CURRENT_TIMESTAMP,
                duration_ms = ?,
                summary = ?
            WHERE run_id = ?
            """,
            (status, error_class, duration_ms, summary, run_id),
        )
        conn.commit()
    finally:
        conn.close()


@contextmanager
def run_context(component: str, op: str, *, meta: Optional[Dict[str, Any]] = None) -> Generator[RunHandle, None, None]:
    h = start_run(component, op, meta=meta)
    try:
        yield h
        h.ok()
    except sqlite3.OperationalError as e:
        # classify DB lock/busy as transient
        msg = str(e).lower()
        if "locked" in msg or "busy" in msg:
            h.fail(error_class="transient", summary=f"{type(e).__name__}: {e}")
        else:
            h.fail(error_class="permanent", summary=f"{type(e).__name__}: {e}")
        raise
    except Exception as e:
        h.fail(error_class="permanent", summary=f"{type(e).__name__}: {e}")
        raise
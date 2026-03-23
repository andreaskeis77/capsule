# FILE: src/run_registry.py
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Optional

from src import settings
from src.db_schema import ensure_schema
from src.run_registry_metrics import compute_kpis_from_runs
from src.run_registry_redaction import REDACT_PLACEHOLDER, safe_json_dumps


VALID_RUN_STATUSES = {"started", "ok", "failed", "partial"}


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception:
        pass
    return conn


# Backward-compatible alias kept for callers/tests that import the old helper.
_safe_json = safe_json_dumps


def _parse_meta_json(raw: Optional[str]) -> Dict[str, Any]:
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def classify_error_class(exc: BaseException) -> str:
    if isinstance(exc, sqlite3.OperationalError):
        msg = str(exc).lower()
        if "locked" in msg or "busy" in msg:
            return "transient"
    return "permanent"


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
        finish_run(
            self.run_id,
            status="failed",
            error_class=error_class,
            duration_ms=self._duration_ms(),
            summary=summary,
        )

    def partial(self, summary: str | None = None) -> None:
        finish_run(
            self.run_id,
            status="partial",
            error_class="permanent",
            duration_ms=self._duration_ms(),
            summary=summary,
        )

    def _duration_ms(self) -> int:
        return int((time.perf_counter() - self._t0) * 1000)


def start_run(component: str, op: str, *, meta: Optional[Dict[str, Any]] = None) -> RunHandle:
    ensure_schema()
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
            (run_id, component, op, "started", safe_json_dumps(meta or {})),
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
            (run_id, level.upper(), event, message, safe_json_dumps(data) if data is not None else None),
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
    if status not in VALID_RUN_STATUSES:
        raise ValueError(f"Invalid run status: {status}")

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
    handle = start_run(component, op, meta=meta)
    try:
        yield handle
        handle.ok()
    except Exception as exc:
        handle.fail(error_class=classify_error_class(exc), summary=f"{type(exc).__name__}: {exc}")
        raise


def list_runs(
    *,
    limit: int = 50,
    offset: int = 0,
    component: Optional[str] = None,
    status: Optional[str] = None,
    op: Optional[str] = None,
    since_hours: Optional[int] = None,
) -> List[Dict[str, Any]]:
    ensure_schema()

    where: List[str] = []
    params: List[Any] = []

    if component:
        where.append("component = ?")
        params.append(component)
    if status:
        where.append("status = ?")
        params.append(status)
    if op:
        where.append("op = ?")
        params.append(op)
    if since_hours is not None:
        dt = datetime.now() - timedelta(hours=since_hours)
        where.append("started_at >= ?")
        params.append(dt.strftime("%Y-%m-%d %H:%M:%S"))

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT run_id, component, op, status, error_class, started_at, finished_at, duration_ms, summary, meta_json
        FROM runs
        {where_sql}
        ORDER BY started_at DESC
        LIMIT ? OFFSET ?
    """
    params.extend([int(limit), int(offset)])

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        out: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["meta"] = _parse_meta_json(item.get("meta_json"))
            out.append(item)
        return out
    finally:
        conn.close()


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    ensure_schema()

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT run_id, component, op, status, error_class, started_at, finished_at, duration_ms, summary, meta_json
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        item = dict(row)
        item["meta"] = _parse_meta_json(item.get("meta_json"))
        return item
    finally:
        conn.close()


def list_events(run_id: str, *, limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
    ensure_schema()

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, run_id, ts, level, event, message, data_json
            FROM run_events
            WHERE run_id = ?
            ORDER BY id ASC
            LIMIT ? OFFSET ?
            """,
            (run_id, int(limit), int(offset)),
        )
        rows = cur.fetchall()
        out: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["data"] = json.loads(item.get("data_json") or "null")
            except Exception:
                item["data"] = None
            out.append(item)
        return out
    finally:
        conn.close()


def compute_kpis(*, since_hours: Optional[int] = None, component: Optional[str] = None) -> Dict[str, Any]:
    runs = list_runs(limit=5000, offset=0, component=component, since_hours=since_hours)
    return compute_kpis_from_runs(runs, since_hours=since_hours, component=component)

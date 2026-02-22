# FILE: src/run_registry.py
from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Optional, Set

from src import settings
from src.db_schema import ensure_schema


REDACT_PLACEHOLDER = "***REDACTED***"

# key tokens are matched on a normalized key: non-alnum -> "_", lowercased.
_SENSITIVE_KEY_TOKENS: Set[str] = {
    "api_key",
    "openai_api_key",
    "authorization",
    "bearer",
    "bearer_token",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "password",
    "cookie",
    "session",
    "private_key",
}


def _norm_key(k: Any) -> str:
    s = str(k)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _is_sensitive_key(k: Any) -> bool:
    nk = _norm_key(k)
    return any(tok in nk for tok in _SENSITIVE_KEY_TOKENS)


def _redact(obj: Any) -> Any:
    """
    Recursively redact secrets from dict/list structures based on key names.
    - dict keys that look sensitive are replaced with REDACT_PLACEHOLDER
    - nested structures are handled recursively
    """
    if obj is None:
        return None

    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if _is_sensitive_key(k):
                out[str(k)] = REDACT_PLACEHOLDER
            else:
                out[str(k)] = _redact(v)
        return out

    if isinstance(obj, (list, tuple)):
        return [_redact(x) for x in obj]

    # primitive types (str/int/bool/float) are safe unless attached to sensitive key above
    return obj


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
    """
    JSON serializer used for meta_json/data_json. Applies secret redaction first.
    """
    obj = _redact(obj)
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        return json.dumps({"_unserializable": str(obj)}, ensure_ascii=False, separators=(",", ":"))


def _parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


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
        msg = str(e).lower()
        if "locked" in msg or "busy" in msg:
            h.fail(error_class="transient", summary=f"{type(e).__name__}: {e}")
        else:
            h.fail(error_class="permanent", summary=f"{type(e).__name__}: {e}")
        raise
    except Exception as e:
        h.fail(error_class="permanent", summary=f"{type(e).__name__}: {e}")
        raise


# -------------------------
# Read/query helpers
# -------------------------

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
        for r in rows:
            d = dict(r)
            try:
                d["meta"] = json.loads(d.get("meta_json") or "{}")
            except Exception:
                d["meta"] = {}
            out.append(d)
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
            FROM runs WHERE run_id = ?
            """,
            (run_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["meta"] = json.loads(d.get("meta_json") or "{}")
        except Exception:
            d["meta"] = {}
        return d
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
        for r in rows:
            d = dict(r)
            try:
                d["data"] = json.loads(d.get("data_json") or "null")
            except Exception:
                d["data"] = None
            out.append(d)
        return out
    finally:
        conn.close()


def compute_kpis(*, since_hours: Optional[int] = None, component: Optional[str] = None) -> Dict[str, Any]:
    runs = list_runs(limit=5000, offset=0, component=component, since_hours=since_hours)
    total = len(runs)
    counts = {"ok": 0, "failed": 0, "partial": 0, "started": 0}
    for r in runs:
        st = (r.get("status") or "").lower()
        if st in counts:
            counts[st] += 1
        else:
            counts.setdefault(st, 0)
            counts[st] += 1

    def rate(x: int) -> Optional[float]:
        return (x / total) if total else None

    ordered = sorted(runs, key=lambda r: (r.get("started_at") or ""))
    mttr_minutes: List[float] = []

    ok_starts: List[datetime] = []
    for r in ordered:
        if (r.get("status") or "").lower() == "ok":
            ts = _parse_ts(r.get("started_at"))
            if ts:
                ok_starts.append(ts)

    for r in ordered:
        if (r.get("status") or "").lower() != "failed":
            continue
        fail_finished = _parse_ts(r.get("finished_at")) or _parse_ts(r.get("started_at"))
        if not fail_finished:
            continue
        nxt = next((t for t in ok_starts if t > fail_finished), None)
        if nxt:
            mttr_minutes.append((nxt - fail_finished).total_seconds() / 60.0)

    latest_ok = next((r for r in runs if (r.get("status") or "").lower() == "ok"), None)
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
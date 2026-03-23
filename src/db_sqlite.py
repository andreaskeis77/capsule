from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Set


def connect_sqlite(db_path: Path | str, *, timeout: float = 5.0) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=timeout)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    )
    return cur.fetchone() is not None


def table_columns(cur: sqlite3.Cursor, table: str) -> Set[str]:
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    return {str(r[1]) for r in rows}


def connect_default(
    db_path: Optional[Path | str] = None,
    *,
    timeout: float = 5.0,
) -> sqlite3.Connection:
    from src import settings

    resolved = Path(db_path) if db_path is not None else Path(settings.DB_PATH)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return connect_sqlite(resolved, timeout=timeout)

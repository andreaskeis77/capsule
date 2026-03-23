from __future__ import annotations

import sqlite3
from typing import Iterable, List

SCHEMA_BASELINE_VERSION = "2026-03-22-tranche-h"


def ensure_schema_migrations_table(cur: sqlite3.Cursor) -> bool:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
        """
    )
    return cur.rowcount != -1


def list_applied_migrations(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    conn.commit()
    cur.execute("SELECT version FROM schema_migrations ORDER BY version")
    return [str(r[0]) for r in cur.fetchall()]


def has_migration(conn: sqlite3.Connection, version: str) -> bool:
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    conn.commit()
    cur.execute(
        "SELECT 1 FROM schema_migrations WHERE version = ? LIMIT 1",
        (version,),
    )
    return cur.fetchone() is not None


def record_migration(
    conn: sqlite3.Connection,
    *,
    version: str,
    notes: str = "",
) -> bool:
    cur = conn.cursor()
    ensure_schema_migrations_table(cur)
    cur.execute(
        """
        INSERT OR IGNORE INTO schema_migrations(version, notes)
        VALUES (?, ?)
        """,
        (version, notes or None),
    )
    conn.commit()
    return cur.rowcount > 0


def record_baseline_if_needed(
    conn: sqlite3.Connection,
    *,
    version: str = SCHEMA_BASELINE_VERSION,
    changes: Iterable[str] | None = None,
) -> bool:
    notes = ""
    if changes:
        notes = ";".join(sorted(str(c) for c in changes))
    return record_migration(conn, version=version, notes=notes)

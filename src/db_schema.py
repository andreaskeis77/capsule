# FILE: src/db_schema.py
from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src import settings

logger = logging.getLogger("WardrobeDB")

# Canonical Items schema (minimal, evolvable, no ORM)
_ITEMS_REQUIRED_COLS: Set[str] = {"id", "user_id", "name"}

# Columns that are safe to ADD if missing (SQLite supports ADD COLUMN easily).
# Keep this aligned with what API v2 reads/writes + ingest metadata + UI editable fields.
_ITEMS_ADDABLE_COLUMNS: Dict[str, str] = {
    "brand": "brand TEXT",
    "category": "category TEXT",
    "color_primary": "color_primary TEXT",
    "color_variant": "color_variant TEXT",
    "needs_review": "needs_review INTEGER DEFAULT 0",
    "material_main": "material_main TEXT",
    "fit": "fit TEXT",
    "collar": "collar TEXT",
    "price": "price TEXT",
    "vision_description": "vision_description TEXT",
    "image_path": "image_path TEXT",
    "created_at": "created_at TEXT DEFAULT CURRENT_TIMESTAMP",
    # UI / planning fields
    "context": "context TEXT",  # "private" | "executive" | NULL
    "size": "size TEXT",
    "notes": "notes TEXT",
    # ingest idempotence + recovery (internal)
    "source_fingerprint": "source_fingerprint TEXT",
    "ingest_status": "ingest_status TEXT",
    "ingest_run_id": "ingest_run_id TEXT",
    "ingest_error": "ingest_error TEXT",
}

_CREATE_ITEMS_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,

    brand TEXT,
    category TEXT,
    color_primary TEXT,
    material_main TEXT,
    fit TEXT,
    collar TEXT,
    price TEXT,
    vision_description TEXT,

    image_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    color_variant TEXT,
    needs_review INTEGER DEFAULT 0,

    context TEXT,
    size TEXT,
    notes TEXT,

    source_fingerprint TEXT,
    ingest_status TEXT,
    ingest_run_id TEXT,
    ingest_error TEXT
)
""".strip()

_CREATE_RUNS_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    component TEXT NOT NULL,
    op TEXT NOT NULL,
    status TEXT NOT NULL,
    error_class TEXT,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    duration_ms INTEGER,
    summary TEXT,
    meta_json TEXT
)
""".strip()

_CREATE_RUN_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS run_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,
    event TEXT NOT NULL,
    message TEXT,
    data_json TEXT
)
""".strip()


def _table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def _table_columns(cur: sqlite3.Cursor, table: str) -> Set[str]:
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    return {r[1] for r in rows}


def ensure_schema(
    db_path: Optional[Path] = None,
    *,
    retries: int = 3,
    base_delay_s: float = 0.15,
) -> List[str]:
    """
    Ensure DB schema is present and compatible with current API expectations.

    Critical path: Data Integrity => Fail-Fast if required columns missing.

    Returns:
        list of applied changes (strings), empty if already up-to-date
    """
    path = Path(db_path) if db_path is not None else settings.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    changes: List[str] = []

    for attempt in range(max(1, retries)):
        try:
            conn = sqlite3.connect(str(path), timeout=5)
            try:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                # --- items ---
                if not _table_exists(cur, "items"):
                    cur.execute(_CREATE_ITEMS_SQL)
                    changes.append("create_table:items")

                cols = _table_columns(cur, "items")

                missing_required = sorted(list(_ITEMS_REQUIRED_COLS - cols))
                if missing_required:
                    raise RuntimeError(f"SchemaInvalid: items missing required columns: {missing_required}")

                for col_name, col_sql in _ITEMS_ADDABLE_COLUMNS.items():
                    if col_name not in cols:
                        cur.execute(f"ALTER TABLE items ADD COLUMN {col_sql}")
                        changes.append(f"add_column:items.{col_name}")

                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_needs_review ON items(needs_review)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_ingest_status ON items(ingest_status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_context ON items(context)")
                # Idempotence: allow many NULLs, but non-NULL fingerprint should be unique per user
                cur.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_items_user_fingerprint ON items(user_id, source_fingerprint)"
                )

                # --- run registry ---
                if not _table_exists(cur, "runs"):
                    cur.execute(_CREATE_RUNS_SQL)
                    changes.append("create_table:runs")

                if not _table_exists(cur, "run_events"):
                    cur.execute(_CREATE_RUN_EVENTS_SQL)
                    changes.append("create_table:run_events")

                cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_component_started ON runs(component, started_at)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_status_started ON runs(status, started_at)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_run_events_run_ts ON run_events(run_id, ts)")

                conn.commit()
            finally:
                conn.close()

            logger.info(
                "DB schema ensured",
                extra={"request_id": "-", "event": "db.schema.ensure", "db": str(path), "changes": changes},
            )
            return changes

        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if ("locked" in msg or "busy" in msg) and attempt < retries - 1:
                time.sleep(base_delay_s * (2**attempt))
                continue
            raise

        except Exception:
            logger.exception("DB schema ensure failed (fail-fast)", extra={"request_id": "-", "event": "db.schema.failed"})
            raise

    return changes
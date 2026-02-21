# FILE: src/db_schema.py
from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from src import settings

logger = logging.getLogger("WardrobeDB")

# Canonical Items schema (minimal, evolvable, no ORM)
# Notes:
# - We only "ALTER TABLE ADD COLUMN" for non-critical/optional columns.
# - If required columns are missing, we FAIL FAST (data integrity critical path).
_ITEMS_REQUIRED_COLS: Set[str] = {"id", "user_id", "name"}

# Columns that are safe to ADD if missing (SQLite supports ADD COLUMN easily).
# Keep this aligned with what API v2 reads/writes.
_ITEMS_ADDABLE_COLUMNS: Dict[str, str] = {
    # core descriptive fields
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
    # timestamps
    "created_at": "created_at TEXT DEFAULT CURRENT_TIMESTAMP",
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
    needs_review INTEGER DEFAULT 0
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
    last_exc: Optional[BaseException] = None

    for attempt in range(max(1, retries)):
        try:
            conn = sqlite3.connect(str(path), timeout=5)
            try:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                # Create table if missing
                if not _table_exists(cur, "items"):
                    cur.execute(_CREATE_ITEMS_SQL)
                    changes.append("create_table:items")

                cols = _table_columns(cur, "items")

                # Contract check: required columns must exist
                missing_required = sorted(list(_ITEMS_REQUIRED_COLS - cols))
                if missing_required:
                    raise RuntimeError(f"SchemaInvalid: items missing required columns: {missing_required}")

                # Add missing optional columns
                for col_name, col_sql in _ITEMS_ADDABLE_COLUMNS.items():
                    if col_name not in cols:
                        cur.execute(f"ALTER TABLE items ADD COLUMN {col_sql}")
                        changes.append(f"add_column:items.{col_name}")

                # Indexes (idempotent)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_items_needs_review ON items(needs_review)")

                conn.commit()
            finally:
                conn.close()

            # Log once (startup typically)
            if changes:
                logger.info(
                    f"DB schema ensured db={path} changes={changes}",
                    extra={"request_id": "-"},
                )
            else:
                logger.info(
                    f"DB schema already up to date db={path}",
                    extra={"request_id": "-"},
                )
            return changes

        except sqlite3.OperationalError as e:
            # Transient class: db locked/busy => retry
            last_exc = e
            msg = str(e).lower()
            if ("locked" in msg or "busy" in msg) and attempt < retries - 1:
                time.sleep(base_delay_s * (2**attempt))
                continue
            raise

        except Exception as e:
            # Permanent class: fail-fast
            last_exc = e
            logger.exception(
                "DB schema ensure failed (fail-fast)",
                extra={"request_id": "-"},
            )
            raise

    # Should never be reached, but keep contract explicit
    if last_exc:
        raise last_exc
    return []

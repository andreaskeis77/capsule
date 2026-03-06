from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional, Sequence

INDEX_SELECT_SQL = """
SELECT id, user_id, name, brand, category, color_primary, color_variant,
       needs_review, context, size, notes, image_path
FROM items
WHERE user_id = ?
ORDER BY id DESC
"""

LEGACY_INVENTORY_COLUMNS: List[str] = [
    "id",
    "name",
    "category",
    "color_primary",
    "color_variant",
    "needs_review",
    "context",
    "size",
    "notes",
    "image_path",
]


def fetch_dashboard_index_rows(conn: sqlite3.Connection, user: str) -> Sequence[sqlite3.Row]:
    """Fetch the index/dashboard rows in the same order and shape as the legacy controller."""
    return conn.execute(INDEX_SELECT_SQL, (user,)).fetchall()


def fetch_item_row_by_id(conn: sqlite3.Connection, item_id: int) -> Optional[sqlite3.Row]:
    """Return a single item row by id or None if it does not exist."""
    return conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    cols: set[str] = set()
    for row in rows:
        if isinstance(row, sqlite3.Row):
            cols.add(str(row["name"]))
        else:
            cols.add(str(row[1]))
    return cols


def fetch_legacy_inventory_items(conn: sqlite3.Connection, user: str) -> List[Dict[str, object]]:
    """Fetch legacy /api/v1/inventory payload rows with backward-compatible dynamic projection.

    The old controller projected a fixed set of wanted columns and substituted
    `NULL AS <col>` for columns that are missing in older schemas. This helper
    preserves that behavior so the route can stay thin.
    """
    cols = _table_columns(conn, "items")
    select_exprs = [col if col in cols else f"NULL AS {col}" for col in LEGACY_INVENTORY_COLUMNS]
    sql = "SELECT " + ", ".join(select_exprs) + " FROM items WHERE user_id = ?"
    rows = conn.execute(sql, (user,)).fetchall()
    return [dict(row) for row in rows]


__all__ = [
    "INDEX_SELECT_SQL",
    "LEGACY_INVENTORY_COLUMNS",
    "fetch_dashboard_index_rows",
    "fetch_item_row_by_id",
    "fetch_legacy_inventory_items",
]

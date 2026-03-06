from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, List, Optional, Sequence


INDEX_ITEM_COLUMNS: Sequence[str] = (
    "id",
    "user_id",
    "name",
    "brand",
    "category",
    "color_primary",
    "color_variant",
    "needs_review",
    "context",
    "size",
    "notes",
    "image_path",
)

LEGACY_INVENTORY_COLUMNS: Sequence[str] = (
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
)


def _project_columns_sql(
    available_columns: Iterable[str],
    wanted_columns: Sequence[str],
) -> str:
    available = set(available_columns)
    select_parts: List[str] = []
    for col in wanted_columns:
        if col in available:
            select_parts.append(col)
        else:
            select_parts.append(f"NULL AS {col}")
    return ", ".join(select_parts)



def get_table_columns(conn: sqlite3.Connection, table_name: str = "items") -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    columns: set[str] = set()
    for row in rows:
        if isinstance(row, sqlite3.Row):
            columns.add(str(row["name"]))
        else:
            columns.add(str(row[1]))
    return columns



def fetch_dashboard_index_rows(conn: sqlite3.Connection, user: str):
    sql = (
        "SELECT "
        + ", ".join(INDEX_ITEM_COLUMNS)
        + " FROM items WHERE user_id = ? ORDER BY id DESC"
    )
    return conn.execute(sql, (user,)).fetchall()



def fetch_item_row_by_id(conn: sqlite3.Connection, item_id: int):
    return conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()



def fetch_legacy_inventory_items(conn: sqlite3.Connection, user: str) -> List[Dict[str, object]]:
    cols = get_table_columns(conn, "items")
    select_sql = _project_columns_sql(cols, LEGACY_INVENTORY_COLUMNS)
    sql = f"SELECT {select_sql} FROM items WHERE user_id = ?"
    rows = conn.execute(sql, (user,)).fetchall()
    return [dict(row) for row in rows]


__all__ = [
    "INDEX_ITEM_COLUMNS",
    "LEGACY_INVENTORY_COLUMNS",
    "fetch_dashboard_index_rows",
    "fetch_item_row_by_id",
    "fetch_legacy_inventory_items",
    "get_table_columns",
]

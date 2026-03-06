from __future__ import annotations

import sqlite3
from typing import Dict, Iterable, List, Optional, Sequence


DASHBOARD_ITEM_COLUMNS: tuple[str, ...] = (
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

LEGACY_INVENTORY_COLUMNS: tuple[str, ...] = (
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


ItemRow = Dict[str, object]


def _row_to_dict(row: sqlite3.Row | tuple | None) -> Optional[ItemRow]:
    if row is None:
        return None
    return dict(row)


def _select_clause_for_existing_columns(existing_cols: Sequence[str], wanted_cols: Sequence[str]) -> str:
    existing = set(existing_cols)
    select_parts: list[str] = []
    for col in wanted_cols:
        if col in existing:
            select_parts.append(col)
        else:
            select_parts.append(f"NULL AS {col}")
    return ", ".join(select_parts)


def list_dashboard_items_for_user(conn: sqlite3.Connection, user: str) -> List[ItemRow]:
    sql = f"""
        SELECT {', '.join(DASHBOARD_ITEM_COLUMNS)}
        FROM items
        WHERE user_id = ?
        ORDER BY id DESC
    """
    rows = conn.execute(sql, (user,)).fetchall()
    return [dict(row) for row in rows]


def get_item_by_id(conn: sqlite3.Connection, item_id: int) -> Optional[ItemRow]:
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    return _row_to_dict(row)


def list_legacy_inventory_for_user(
    conn: sqlite3.Connection,
    user: str,
    *,
    wanted_cols: Sequence[str] = LEGACY_INVENTORY_COLUMNS,
) -> List[ItemRow]:
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(items)").fetchall()]
    select_clause = _select_clause_for_existing_columns(cols, wanted_cols)
    sql = f"SELECT {select_clause} FROM items WHERE user_id = ?"
    rows = conn.execute(sql, (user,)).fetchall()
    return [dict(row) for row in rows]


__all__ = [
    "DASHBOARD_ITEM_COLUMNS",
    "LEGACY_INVENTORY_COLUMNS",
    "ItemRow",
    "get_item_by_id",
    "list_dashboard_items_for_user",
    "list_legacy_inventory_for_user",
]

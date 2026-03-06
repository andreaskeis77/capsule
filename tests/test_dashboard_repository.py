from __future__ import annotations

import sqlite3

from src.dashboard_repository import (
    fetch_dashboard_index_rows,
    fetch_item_row_by_id,
    fetch_legacy_inventory_items,
    get_table_columns,
)



def _make_conn(with_full_schema: bool = True) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    if with_full_schema:
        conn.execute(
            """
            CREATE TABLE items (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                brand TEXT,
                category TEXT,
                color_primary TEXT,
                color_variant TEXT,
                needs_review INTEGER,
                context TEXT,
                size TEXT,
                notes TEXT,
                image_path TEXT
            )
            """
        )
    else:
        conn.execute(
            """
            CREATE TABLE items (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                category TEXT
            )
            """
        )
    return conn



def test_get_table_columns_reads_schema_names():
    conn = _make_conn()
    cols = get_table_columns(conn)
    assert "id" in cols
    assert "user_id" in cols
    assert "image_path" in cols



def test_fetch_dashboard_index_rows_orders_desc_for_user():
    conn = _make_conn()
    conn.executemany(
        """
        INSERT INTO items (
            id, user_id, name, brand, category, color_primary, color_variant,
            needs_review, context, size, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "karen", "A", "", "cat_blouses", "blue", "", 0, "office", "40", "", "a"),
            (2, "other", "B", "", "cat_blouses", "blue", "", 0, "office", "40", "", "b"),
            (3, "karen", "C", "", "cat_jackets", "black", "", 1, "casual", "42", "", "c"),
        ],
    )

    rows = fetch_dashboard_index_rows(conn, "karen")
    assert [row["id"] for row in rows] == [3, 1]
    assert rows[0]["name"] == "C"



def test_fetch_item_row_by_id_returns_row_or_none():
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO items (
            id, user_id, name, brand, category, color_primary, color_variant,
            needs_review, context, size, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (7, "karen", "Cape", "", "poncho", "red", "", 0, "casual", "L", "", "img/7"),
    )

    row = fetch_item_row_by_id(conn, 7)
    assert row is not None
    assert row["name"] == "Cape"
    assert fetch_item_row_by_id(conn, 999) is None



def test_fetch_legacy_inventory_items_backfills_missing_columns_with_null():
    conn = _make_conn(with_full_schema=False)
    conn.executemany(
        "INSERT INTO items (id, user_id, name, category) VALUES (?, ?, ?, ?)",
        [
            (1, "karen", "Bluse", "cat_blouses"),
            (2, "other", "Jacke", "cat_jackets"),
        ],
    )

    items = fetch_legacy_inventory_items(conn, "karen")
    assert len(items) == 1
    item = items[0]
    assert item["id"] == 1
    assert item["name"] == "Bluse"
    assert item["category"] == "cat_blouses"
    assert item["color_primary"] is None
    assert item["image_path"] is None

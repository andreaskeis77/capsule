import sqlite3

from src.dashboard_repository import (
    DASHBOARD_ITEM_COLUMNS,
    LEGACY_INVENTORY_COLUMNS,
    get_item_by_id,
    list_dashboard_items_for_user,
    list_legacy_inventory_for_user,
)


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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
    return conn


def test_list_dashboard_items_for_user_returns_expected_projection_in_desc_order():
    conn = _make_conn()
    conn.executemany(
        """
        INSERT INTO items (
            id, user_id, name, brand, category, color_primary, color_variant,
            needs_review, context, size, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "karen", "A", "B1", "cat_blouses", "blue", "navy", 0, "business", "40", "n1", "img/a"),
            (2, "karen", "C", "B2", "cat_jackets", "black", "", 1, "private", "42", "n2", "img/c"),
            (3, "other", "D", "B3", "cat_coats", "red", "", 0, "private", "44", "n3", "img/d"),
        ],
    )
    conn.commit()

    rows = list_dashboard_items_for_user(conn, "karen")

    assert [r["id"] for r in rows] == [2, 1]
    assert set(rows[0].keys()) == set(DASHBOARD_ITEM_COLUMNS)
    assert rows[0]["name"] == "C"



def test_get_item_by_id_returns_full_row_dict_or_none():
    conn = _make_conn()
    conn.execute(
        """
        INSERT INTO items (
            id, user_id, name, brand, category, color_primary, color_variant,
            needs_review, context, size, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (7, "karen", "Poncho", "Brand", "poncho", "beige", "", 1, "private", "L", "x", "img/p"),
    )
    conn.commit()

    found = get_item_by_id(conn, 7)
    missing = get_item_by_id(conn, 999)

    assert found is not None
    assert found["name"] == "Poncho"
    assert found["category"] == "poncho"
    assert missing is None



def test_list_legacy_inventory_for_user_fills_missing_columns_with_null_aliases():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            category TEXT,
            notes TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO items (id, user_id, name, category, notes) VALUES (?, ?, ?, ?, ?)",
        (1, "karen", "Minimal", "cat_knitwear", "hello"),
    )
    conn.commit()

    rows = list_legacy_inventory_for_user(conn, "karen")

    assert len(rows) == 1
    row = rows[0]
    assert set(row.keys()) == set(LEGACY_INVENTORY_COLUMNS)
    assert row["id"] == 1
    assert row["name"] == "Minimal"
    assert row["category"] == "cat_knitwear"
    assert row["notes"] == "hello"
    assert row["color_primary"] is None
    assert row["image_path"] is None

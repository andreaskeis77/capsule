from __future__ import annotations

import sqlite3

from src.dashboard_repository import (
    LEGACY_INVENTORY_COLUMNS,
    fetch_dashboard_index_rows,
    fetch_item_row_by_id,
    fetch_legacy_inventory_items,
)


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


def test_fetch_dashboard_index_rows_orders_desc_and_scopes_user():
    conn = _make_conn()
    conn.executescript(
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
        );
        INSERT INTO items (id, user_id, name, category, needs_review, context) VALUES
            (1, 'karen', 'Older', 'Blusen', 0, 'business'),
            (2, 'karen', 'Newer', 'Jacken', 1, 'private'),
            (3, 'other', 'Ignored', 'Hosen', 0, 'private');
        """
    )

    rows = fetch_dashboard_index_rows(conn, 'karen')
    names = [row['name'] for row in rows]

    assert names == ['Newer', 'Older']


def test_fetch_item_row_by_id_returns_row_or_none():
    conn = _make_conn()
    conn.executescript(
        """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            category TEXT
        );
        INSERT INTO items (id, user_id, name, category) VALUES (10, 'karen', 'Blazer', 'Jacken');
        """
    )

    row = fetch_item_row_by_id(conn, 10)
    missing = fetch_item_row_by_id(conn, 99)

    assert row is not None
    assert row['name'] == 'Blazer'
    assert missing is None


def test_fetch_legacy_inventory_items_projects_missing_columns_as_null():
    conn = _make_conn()
    conn.executescript(
        """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            category TEXT,
            context TEXT
        );
        INSERT INTO items (id, user_id, name, category, context) VALUES
            (1, 'karen', 'Poncho', 'poncho', 'private'),
            (2, 'other', 'Ignore', 'Hosen', 'business');
        """
    )

    items = fetch_legacy_inventory_items(conn, 'karen')

    assert len(items) == 1
    item = items[0]
    assert list(item.keys()) == LEGACY_INVENTORY_COLUMNS
    assert item['id'] == 1
    assert item['name'] == 'Poncho'
    assert item['category'] == 'poncho'
    assert item['context'] == 'private'
    assert item['notes'] is None
    assert item['image_path'] is None

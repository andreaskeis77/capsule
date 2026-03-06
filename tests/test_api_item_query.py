import sqlite3

from src.api_item_query import (
    count_review_rows,
    fetch_item_image_ref_by_id,
    fetch_item_row_by_id,
    item_row_to_payload,
    item_summary_row_to_payload,
    list_item_summary_rows,
    list_review_rows,
    review_row_to_payload,
)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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
            material_main TEXT,
            fit TEXT,
            collar TEXT,
            price TEXT,
            vision_description TEXT,
            image_path TEXT,
            created_at TEXT,
            context TEXT,
            size TEXT,
            notes TEXT
        );
        """
    )
    conn.executemany(
        """
        INSERT INTO items (
            id, user_id, name, brand, category, color_primary, color_variant, needs_review,
            material_main, fit, collar, price, vision_description, image_path, created_at,
            context, size, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "karen", "Blue Blazer", "Boss", "cat_blazer", "blue", "navy", 1, "wool", None, None, None, None, "karen/blue_blazer_1", "2026-01-01", "executive", "48", "note a"),
            (2, "karen", "Red Dress", "", "cat_dress", "red", None, 0, None, None, None, None, None, None, "2026-01-02", "private", None, None),
            (3, "andreas", "Green Shirt", "", "cat_shirt", "green", None, 1, None, None, None, None, None, "andreas/green_shirt_3", "2026-01-03", None, None, None),
        ],
    )
    return conn


def test_fetch_helpers_by_id():
    conn = _conn()
    row = fetch_item_row_by_id(conn, 1)
    assert row is not None
    assert row["name"] == "Blue Blazer"

    image_ref = fetch_item_image_ref_by_id(conn, 1)
    assert image_ref is not None
    assert image_ref["image_path"] == "karen/blue_blazer_1"



def test_list_and_count_review_rows_are_scoped_and_sorted():
    conn = _conn()
    summary_rows = list_item_summary_rows(conn, "karen")
    assert [r["id"] for r in summary_rows] == [2, 1]

    assert count_review_rows(conn, "karen") == 1
    review_rows = list_review_rows(conn, "karen", limit=10, offset=0)
    assert [r["id"] for r in review_rows] == [1]



def test_payload_serializers_shape_expected_response_data():
    conn = _conn()
    row = fetch_item_row_by_id(conn, 1)
    assert row is not None

    item_payload = item_row_to_payload(row, "http://testserver")
    assert item_payload["id"] == 1
    assert item_payload["main_image_url"] == "http://testserver/images/karen/blue_blazer_1/main.jpg"
    assert item_payload["image_urls"] == ["http://testserver/images/karen/blue_blazer_1/main.jpg"]
    assert item_payload["needs_review"] == 1
    assert item_payload["context"] == "executive"

    summary_payload = item_summary_row_to_payload(row)
    assert summary_payload == {
        "id": 1,
        "name": "Blue Blazer",
        "category": "cat_blazer",
        "color_primary": "blue",
        "color_variant": "navy",
        "needs_review": 1,
        "context": "executive",
    }

    review_payload = review_row_to_payload(row, ["navy", "midnight blue"])
    assert review_payload["suggestions"] == ["navy", "midnight blue"]
    assert review_payload["color_variant"] == "navy"

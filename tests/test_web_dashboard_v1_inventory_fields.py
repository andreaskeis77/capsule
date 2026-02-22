# FILE: tests/test_web_dashboard_v1_inventory_fields.py
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src import settings
from src.db_schema import ensure_schema


@pytest.fixture()
def flask_client(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    img_dir = tmp_path / "images"

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    monkeypatch.setenv("WARDROBE_ENV", "test")

    settings.reload_settings()
    ensure_schema()

    # Insert one item with the new meta fields
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO items (user_id, name, category, color_primary, color_variant, needs_review, context, size, notes, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("karen", "Test Item", "cat_test", "blue", "navy", 1, "executive", "48", "note", "karen/test_item_1"),
    )
    conn.commit()
    conn.close()

    # Import Flask app AFTER env/settings are set
    import sys

    sys.modules.pop("src.web_dashboard", None)
    from src.web_dashboard import flask_app

    with flask_app.test_client() as c:
        yield c


def test_v1_inventory_includes_meta_fields(flask_client):
    r = flask_client.get("/api/v1/inventory?user=karen", headers={"X-API-Key": "testkey"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["user"] == "karen"
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

    it = data["items"][0]
    # core + new fields
    assert "id" in it
    assert it["name"] == "Test Item"
    assert it["context"] == "executive"
    assert it["size"] == "48"
    assert it["notes"] == "note"
    assert it["needs_review"] == 1
    assert it["color_variant"] == "navy"
    assert it["image_path"] == "karen/test_item_1"
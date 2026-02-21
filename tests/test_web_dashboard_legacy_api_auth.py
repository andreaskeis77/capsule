# FILE: tests/test_web_dashboard_legacy_api_auth.py
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


def init_test_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            color_primary TEXT,
            color_variant TEXT,
            needs_review INTEGER DEFAULT 0,
            material_main TEXT,
            fit TEXT,
            collar TEXT,
            price TEXT,
            vision_description TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        "INSERT INTO items (user_id, name, category, color_primary) VALUES (?, ?, ?, ?)",
        ("karen", "Test Item", "cat_test", "blue"),
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def flask_client(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe_webdash.db"
    img_dir = tmp_path / "images"

    init_test_db(db_path)
    img_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    monkeypatch.setenv("WARDROBE_ENV", "test")
    monkeypatch.setenv("WARDROBE_DEBUG", "0")
    monkeypatch.setenv("WARDROBE_MOUNT_FLASK", "0")
    monkeypatch.setenv("WARDROBE_ONTOLOGY_MODE", "off")

    from src import settings as settings_module

    settings_module.reload_settings()

    from src.web_dashboard import flask_app

    return flask_app.test_client()


def test_inventory_requires_api_key(flask_client):
    r = flask_client.get("/api/v1/inventory?user=karen")
    assert r.status_code == 401

    r2 = flask_client.get("/api/v1/inventory?user=karen", headers={"X-API-Key": "wrong"})
    assert r2.status_code == 401


def test_inventory_with_api_key_ok(flask_client):
    r = flask_client.get("/api/v1/inventory?user=karen", headers={"X-API-Key": "testkey"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["user"] == "karen"
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1


def test_item_detail_requires_api_key(flask_client):
    r = flask_client.get("/api/v1/item/1")
    assert r.status_code == 401

    r2 = flask_client.get("/api/v1/item/1", headers={"X-API-Key": "testkey"})
    assert r2.status_code in (200, 404)
    if r2.status_code == 200:
        data = r2.get_json()
        assert data["id"] == 1
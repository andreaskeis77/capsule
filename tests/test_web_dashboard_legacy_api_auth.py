# FILE: tests/test_web_dashboard_legacy_api_auth.py
from __future__ import annotations

import os
import sqlite3
import sys
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


@pytest.fixture(scope="module")
def flask_client(tmp_path_factory):
    root = tmp_path_factory.mktemp("wardrobe_webdash")
    db_path = root / "wardrobe_webdash.db"
    img_dir = root / "images"

    init_test_db(db_path)
    img_dir.mkdir(parents=True, exist_ok=True)

    keys = [
        "WARDROBE_DB_PATH",
        "WARDROBE_IMG_DIR",
        "WARDROBE_API_KEY",
        "WARDROBE_ALLOW_LOCAL_NOAUTH",
        "WARDROBE_ENV",
        "WARDROBE_DEBUG",
        "WARDROBE_MOUNT_FLASK",
        "WARDROBE_ONTOLOGY_MODE",
    ]
    old = {k: os.environ.get(k) for k in keys}

    os.environ["WARDROBE_DB_PATH"] = str(db_path)
    os.environ["WARDROBE_IMG_DIR"] = str(img_dir)
    os.environ["WARDROBE_API_KEY"] = "testkey"
    os.environ["WARDROBE_ALLOW_LOCAL_NOAUTH"] = "0"
    os.environ["WARDROBE_ENV"] = "test"
    os.environ["WARDROBE_DEBUG"] = "0"
    os.environ["WARDROBE_MOUNT_FLASK"] = "0"
    os.environ["WARDROBE_ONTOLOGY_MODE"] = "off"

    # IMPORTANT:
    # Other tests import src.settings first; `from src import settings` can keep a stale
    # package attribute even if sys.modules['src.settings'] was deleted.
    # Purge the whole src package namespace for a clean import under this fixture env.
    for name in list(sys.modules.keys()):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]

    from src.web_dashboard import flask_app

    client = flask_app.test_client()
    yield client

    # restore env
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


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
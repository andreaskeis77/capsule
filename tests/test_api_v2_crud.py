# FILE: tests/test_api_v2_crud.py
from __future__ import annotations

import base64
import io
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


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
    conn.commit()
    conn.close()


def make_test_jpeg_b64(size: tuple[int, int] = (50, 50)) -> str:
    img = Image.new("RGB", size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """
    IMPORTANT:
    src.settings reads env vars at import time and stores DB_PATH/IMG_DIR as module globals.
    Therefore this fixture is module-scoped and sets env once for the whole module.
    """
    root = tmp_path_factory.mktemp("wardrobe_test")
    db_path = root / "wardrobe_test.db"
    img_dir = root / "images"
    trash_dir = root / "trash_images"

    init_test_db(db_path)
    img_dir.mkdir(parents=True, exist_ok=True)
    trash_dir.mkdir(parents=True, exist_ok=True)

    keys = [
        "WARDROBE_DB_PATH",
        "WARDROBE_IMG_DIR",
        "WARDROBE_TRASH_DIR",
        "WARDROBE_API_KEY",
        "WARDROBE_ENV",
        "WARDROBE_DEBUG",
        "WARDROBE_ALLOW_LOCAL_NOAUTH",
        "WARDROBE_MOUNT_FLASK",
        "WARDROBE_MAX_IMAGE_MB",
        "WARDROBE_IMAGE_MAX_DIM",
        "WARDROBE_IMAGE_JPEG_QUALITY",
        "WARDROBE_STORE_ORIGINAL",
        "WARDROBE_ONTOLOGY_MODE",
    ]
    old = {k: os.environ.get(k) for k in keys}

    os.environ["WARDROBE_DB_PATH"] = str(db_path)
    os.environ["WARDROBE_IMG_DIR"] = str(img_dir)
    os.environ["WARDROBE_TRASH_DIR"] = str(trash_dir)

    os.environ["WARDROBE_API_KEY"] = "testkey"
    os.environ["WARDROBE_ENV"] = "test"
    os.environ["WARDROBE_DEBUG"] = "1"
    os.environ["WARDROBE_ALLOW_LOCAL_NOAUTH"] = "0"
    os.environ["WARDROBE_MOUNT_FLASK"] = "0"
    os.environ["WARDROBE_MAX_IMAGE_MB"] = "8"
    os.environ["WARDROBE_IMAGE_MAX_DIM"] = "1600"
    os.environ["WARDROBE_IMAGE_JPEG_QUALITY"] = "85"
    os.environ["WARDROBE_STORE_ORIGINAL"] = "0"

    # IMPORTANT: keep ontology off in CRUD tests
    os.environ["WARDROBE_ONTOLOGY_MODE"] = "off"

    # Force fresh import so settings picks up env reliably
    for mod in ("src.settings", "src.api_v2", "src.api_main"):
        if mod in sys.modules:
            del sys.modules[mod]

    from src.api_main import app

    with TestClient(app) as c:
        yield c

    # restore env
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_health(client):
    r = client.get("/api/v2/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_unauthorized_requires_key(client):
    r = client.get("/api/v2/items?user=karen")
    assert r.status_code == 401


def test_create_update_delete(client):
    b64 = make_test_jpeg_b64()

    payload = {
        "user_id": "karen",
        "name": "Blauer Blazer",
        "brand": "Boss",
        "category": "cat_test",
        "image_main_base64": b64,
        "image_ext": "jpg",
    }
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 200, r.text
    created = r.json()
    assert created["id"] > 0
    assert created["image_path"].startswith("karen/")
    assert created["main_image_url"] is not None
    item_id = created["id"]

    # Folder exists after create
    img_dir = Path(os.environ["WARDROBE_IMG_DIR"])
    folder = img_dir / Path(created["image_path"])
    assert folder.exists()
    assert (folder / "main.jpg").exists()

    r2 = client.patch(
        f"/api/v2/items/{item_id}",
        json={"brand": "Adidas"},
        headers={"X-API-Key": "testkey"},
    )
    assert r2.status_code == 200, r2.text
    updated = r2.json()
    assert updated["brand"] == "Adidas"

    r3 = client.delete(f"/api/v2/items/{item_id}", headers={"X-API-Key": "testkey"})
    assert r3.status_code == 200, r3.text
    assert r3.json()["deleted"] is True

    # Folder should no longer exist in IMG_DIR (moved to trash + best-effort deleted)
    assert not folder.exists()

    # DB row is gone
    conn = sqlite3.connect(os.environ["WARDROBE_DB_PATH"])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    assert row is None


def test_validate_endpoint(client):
    b64 = make_test_jpeg_b64()
    payload = {
        "user_id": "karen",
        "name": "Validate Only",
        "image_main_base64": b64,
    }
    r = client.post("/api/v2/items/validate", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["normalized_image"]["stored_ext"] == "jpg"
    assert data["example_image_path"].startswith("karen/")


def test_invalid_base64(client):
    payload = {"user_id": "karen", "name": "Bad", "image_main_base64": "notbase64"}
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "ImageDecodeFailed"
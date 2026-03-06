# FILE: tests/test_api_v2_crud.py
from __future__ import annotations

import base64
import io
import os
import sqlite3
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


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe_test.db"
    img_dir = tmp_path / "images"
    trash_dir = tmp_path / "trash_images"

    init_test_db(db_path)
    img_dir.mkdir(parents=True, exist_ok=True)
    trash_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_TRASH_DIR", str(trash_dir))

    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ENV", "test")
    monkeypatch.setenv("WARDROBE_DEBUG", "1")
    monkeypatch.setenv("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    monkeypatch.setenv("WARDROBE_MOUNT_FLASK", "0")
    monkeypatch.setenv("WARDROBE_MAX_IMAGE_MB", "8")
    monkeypatch.setenv("WARDROBE_IMAGE_MAX_DIM", "1600")
    monkeypatch.setenv("WARDROBE_IMAGE_JPEG_QUALITY", "85")
    monkeypatch.setenv("WARDROBE_STORE_ORIGINAL", "0")

    monkeypatch.setenv("WARDROBE_ONTOLOGY_MODE", "off")

    from src import settings as settings_module

    settings_module.reload_settings()

    from src import api_v2

    api_v2.init_ontology()

    from src.api_main import app

    with TestClient(app) as c:
        yield c


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
        "context": "executive",
        "size": "48",
        "notes": "Initial note",
        "image_main_base64": b64,
        "image_ext": "jpg",
    }
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 200, r.text
    created = r.json()
    assert created["id"] > 0
    assert created["image_path"].startswith("karen/")
    assert created["main_image_url"] is not None
    assert created["context"] == "executive"
    assert created["size"] == "48"
    assert created["notes"] == "Initial note"

    item_id = created["id"]

    img_dir = Path(os.environ["WARDROBE_IMG_DIR"])
    folder_old = img_dir / Path(created["image_path"])
    assert folder_old.exists()
    assert (folder_old / "main.jpg").exists()

    # Manual meta updates: context/notes + needs_review
    r_meta = client.patch(
        f"/api/v2/items/{item_id}",
        json={"context": "private", "notes": "Updated note", "needs_review": 1},
        headers={"X-API-Key": "testkey"},
    )
    assert r_meta.status_code == 200, r_meta.text
    meta = r_meta.json()
    assert meta["context"] == "private"
    assert meta["notes"] == "Updated note"
    assert meta["needs_review"] == 1

    # Rename triggers folder move
    r_name = client.patch(
        f"/api/v2/items/{item_id}",
        json={"name": "Roter Blazer"},
        headers={"X-API-Key": "testkey"},
    )
    assert r_name.status_code == 200, r_name.text
    renamed = r_name.json()
    assert renamed["name"] == "Roter Blazer"
    assert renamed["image_path"].startswith("karen/")
    assert renamed["image_path"] != created["image_path"]
    assert renamed["context"] == "private"  # persisted
    assert renamed["needs_review"] == 1

    folder_new = img_dir / Path(renamed["image_path"])
    assert folder_new.exists()
    assert (folder_new / "main.jpg").exists()
    assert not folder_old.exists()

    # Move across user roots is still supported by the current API contract.
    r_user = client.patch(
        f"/api/v2/items/{item_id}",
        json={"user_id": "andreas"},
        headers={"X-API-Key": "testkey"},
    )
    assert r_user.status_code == 200, r_user.text
    moved_user = r_user.json()
    assert moved_user["user_id"] == "andreas"
    assert moved_user["image_path"].startswith("andreas/")

    folder_user = img_dir / Path(moved_user["image_path"])
    assert folder_user.exists()
    assert (folder_user / "main.jpg").exists()
    assert not folder_new.exists()

    # Another metadata update
    r2 = client.patch(
        f"/api/v2/items/{item_id}",
        json={"brand": "Adidas", "size": "50"},
        headers={"X-API-Key": "testkey"},
    )
    assert r2.status_code == 200, r2.text
    updated = r2.json()
    assert updated["brand"] == "Adidas"
    assert updated["size"] == "50"
    assert updated["user_id"] == "andreas"

    r3 = client.delete(f"/api/v2/items/{item_id}", headers={"X-API-Key": "testkey"})
    assert r3.status_code == 200, r3.text
    assert r3.json()["deleted"] is True

    assert not folder_user.exists()

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
        "context": "executive",
        "image_main_base64": b64,
    }
    r = client.post("/api/v2/items/validate", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["normalized_image"]["stored_ext"] == "jpg"
    assert data["example_image_path"].startswith("karen/")
    assert data["normalized_fields"]["context"] == "executive"


def test_invalid_base64(client):
    payload = {"user_id": "karen", "name": "Bad", "image_main_base64": "notbase64"}
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "ImageDecodeFailed"
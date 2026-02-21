# FILE: tests/test_api_v2_crud.py
import sqlite3
import base64
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def init_test_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            color_primary TEXT,
            material_main TEXT,
            fit TEXT,
            collar TEXT,
            price TEXT,
            vision_description TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            color_variant TEXT,
            needs_review INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def make_test_jpeg_b64(size=(50, 50)) -> str:
    img = Image.new("RGB", size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe_test.db"
    img_dir = tmp_path / "images"
    init_test_db(db_path)
    img_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ENV", "test")
    monkeypatch.setenv("WARDROBE_DEBUG", "1")
    monkeypatch.setenv("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    monkeypatch.setenv("WARDROBE_MOUNT_FLASK", "0")
    monkeypatch.setenv("WARDROBE_MAX_IMAGE_MB", "8")
    monkeypatch.setenv("WARDROBE_IMAGE_MAX_DIM", "1600")
    monkeypatch.setenv("WARDROBE_IMAGE_JPEG_QUALITY", "85")
    monkeypatch.setenv("WARDROBE_STORE_ORIGINAL", "0")

    # IMPORTANT: keep ontology off in CRUD tests
    monkeypatch.setenv("WARDROBE_ONTOLOGY_MODE", "off")

    from src.api_main import app
    return TestClient(app)


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
    assert "example_image_path" in data
    assert data["normalized_image"]["stored_ext"] == "jpg"


def test_invalid_base64(client):
    payload = {
        "user_id": "karen",
        "name": "Bad",
        "image_main_base64": "!!!notbase64!!!",
    }
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 400

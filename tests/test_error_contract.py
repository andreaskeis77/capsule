# FILE: tests/test_error_contract.py
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


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
    monkeypatch.setenv("WARDROBE_ONTOLOGY_MODE", "off")

    # Refresh settings + ontology for this test environment
    from src import settings as settings_module

    settings_module.reload_settings()

    from src import api_v2

    api_v2.init_ontology()

    from src.api_main import app

    with TestClient(app) as c:
        yield c


def test_unauthorized_has_dict_detail_and_request_id(client):
    r = client.get("/api/v2/items?user=karen")
    assert r.status_code == 401
    data = r.json()
    assert isinstance(data.get("detail"), dict)
    assert data["detail"]["error"] == "Unauthorized"
    assert "request_id" in data["detail"]
    assert data["detail"]["error_class"] == "permanent"


def test_v2_not_found_is_json_dict_even_with_fallback(client):
    r = client.get("/api/v2/this-does-not-exist")
    assert r.status_code == 404
    data = r.json()
    assert isinstance(data.get("detail"), dict)
    assert data["detail"]["error"] == "NotFound"
    assert "request_id" in data["detail"]
    assert data["detail"]["error_class"] == "permanent"


def test_validation_error_is_normalized(client):
    # Missing required field image_main_base64 -> 422 validation
    payload = {"user_id": "karen", "name": "X"}
    r = client.post("/api/v2/items", json=payload, headers={"X-API-Key": "testkey"})
    assert r.status_code == 422
    data = r.json()
    assert isinstance(data.get("detail"), dict)
    assert data["detail"]["error"] == "ValidationError"
    assert "request_id" in data["detail"]
    assert isinstance(data["detail"].get("issues"), list)
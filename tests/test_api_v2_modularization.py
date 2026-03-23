from __future__ import annotations

from pathlib import Path

from src import settings as settings_module
from src import api_v2


def test_api_v2_router_exposes_expected_paths():
    paths = {route.path for route in api_v2.router.routes}
    assert "/api/v2/health" in paths
    assert "/api/v2/items" in paths
    assert "/api/v2/items/review" in paths
    assert "/api/v2/items/{item_id}" in paths
    assert "/api/v2/items/validate" in paths


def test_api_v2_shim_exposes_live_ontology_state(monkeypatch, tmp_path):
    db_path = tmp_path / "wardrobe_test.db"
    img_dir = tmp_path / "images"
    trash_dir = tmp_path / "trash"

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_TRASH_DIR", str(trash_dir))
    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ONTOLOGY_MODE", "off")

    settings_module.reload_settings()
    api_v2.init_ontology()

    assert api_v2.ONTOLOGY is None


def test_api_v2_keeps_contract_constants():
    assert api_v2.VALID_USERS == {"andreas", "karen"}
    assert api_v2.VALID_CONTEXTS == {"private", "executive"}
    assert "notes" in api_v2.API_V2_ITEM_MUTATION_SHAPE.allowed_fields

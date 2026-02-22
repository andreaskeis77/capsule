# FILE: tests/test_admin_item_edit_context_select.py
from __future__ import annotations

import re
import sqlite3
import sys

import pytest

from src import settings
from src.db_schema import ensure_schema


@pytest.fixture()
def flask_client(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    img_dir = tmp_path / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_API_KEY", "testkey")
    monkeypatch.setenv("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    monkeypatch.setenv("WARDROBE_ENV", "test")

    settings.reload_settings()
    ensure_schema()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (user_id, name, category, color_primary, context, needs_review) VALUES (?,?,?,?,?,?)",
        ("karen", "ZZ_EDIT_ITEM", "cat_test", "blue", "executive", 1),
    )
    item_id = cur.lastrowid
    conn.commit()
    conn.close()

    sys.modules.pop("src.web_dashboard", None)
    from src.web_dashboard import flask_app

    with flask_app.test_client() as c:
        c._test_item_id = item_id  # type: ignore[attr-defined]
        yield c


def test_admin_edit_renders_context_select(flask_client):
    item_id = flask_client._test_item_id  # type: ignore[attr-defined]
    r = flask_client.get(f"/admin/item/{item_id}?user=karen", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert r.status_code == 200
    html = r.get_data(as_text=True)

    assert 'name="context"' in html
    assert re.search(r'<select[^>]+name="context"', html) is not None
    assert re.search(r'<option[^>]*value="executive"[^>]*selected', html) is not None

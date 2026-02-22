# FILE: tests/test_dashboard_index_filters.py
from __future__ import annotations

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
        ("karen", "ZZ_EXEC_REVIEW", "cat_test", "blue", "executive", 1),
    )
    cur.execute(
        "INSERT INTO items (user_id, name, category, color_primary, context, needs_review) VALUES (?,?,?,?,?,?)",
        ("karen", "ZZ_EXEC_OK", "cat_test", "blue", "executive", 0),
    )
    cur.execute(
        "INSERT INTO items (user_id, name, category, color_primary, context, needs_review) VALUES (?,?,?,?,?,?)",
        ("karen", "ZZ_PRIV_REVIEW", "cat_test", "blue", "private", 1),
    )
    conn.commit()
    conn.close()

    sys.modules.pop("src.web_dashboard", None)
    from src.web_dashboard import flask_app

    with flask_app.test_client() as c:
        yield c


def test_index_filters_context_and_review(flask_client):
    r = flask_client.get("/?user=karen&ctx=executive&review=1")
    assert r.status_code == 200
    html = r.get_data(as_text=True)

    assert "ZZ_EXEC_REVIEW" in html
    assert "ZZ_EXEC_OK" not in html
    assert "ZZ_PRIV_REVIEW" not in html


def test_index_filters_context_only(flask_client):
    r = flask_client.get("/?user=karen&ctx=private")
    assert r.status_code == 200
    html = r.get_data(as_text=True)

    assert "ZZ_PRIV_REVIEW" in html
    assert "ZZ_EXEC_REVIEW" not in html
    assert "ZZ_EXEC_OK" not in html

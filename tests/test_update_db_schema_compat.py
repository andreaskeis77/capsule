from __future__ import annotations

import sqlite3
from pathlib import Path

from src import settings
from src.update_db_schema import update_schema


def _create_legacy_items_table(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _get_columns(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(items)")
        return {str(r[1]) for r in cur.fetchall()}
    finally:
        conn.close()


def test_update_schema_routes_to_ensure_schema(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy.db"
    _create_legacy_items_table(db_path)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()

    changes = update_schema()

    cols = _get_columns(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        tables = {
            str(r[0])
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert "brand" in cols
    assert "image_path" in cols
    assert "ingest_status" in cols
    assert "runs" in tables
    assert "run_events" in tables
    assert "schema_migrations" in tables
    assert changes

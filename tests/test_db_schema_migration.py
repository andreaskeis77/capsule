# FILE: tests/test_db_schema_migration.py
import os
import sqlite3
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema


def _create_legacy_items_table(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
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
    conn.close()


def _get_cols(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(items)")
    cols = {r[1] for r in cur.fetchall()}
    conn.close()
    return cols


def test_ensure_schema_adds_missing_columns(tmp_path, monkeypatch):
    legacy_db = tmp_path / "legacy_wardrobe.db"
    _create_legacy_items_table(legacy_db)

    orig_db_env = os.environ.get("WARDROBE_DB_PATH")
    try:
        monkeypatch.setenv("WARDROBE_DB_PATH", str(legacy_db))
        settings.reload_settings()

        ensure_schema()

        cols = _get_cols(legacy_db)
        assert "color_variant" in cols
        assert "needs_review" in cols
        assert "created_at" in cols
        assert "image_path" in cols
        assert "vision_description" in cols
        assert "context" in cols
        assert "size" in cols
        assert "notes" in cols
    finally:
        if orig_db_env is None:
            monkeypatch.delenv("WARDROBE_DB_PATH", raising=False)
        else:
            monkeypatch.setenv("WARDROBE_DB_PATH", orig_db_env)
        settings.reload_settings()
from __future__ import annotations

import sqlite3
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema
from src.db_schema_migrations import SCHEMA_BASELINE_VERSION, list_applied_migrations


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def test_ensure_schema_creates_schema_migrations_table(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()

    changes = ensure_schema()

    conn = _connect(db_path)
    try:
        tables = {
            str(r["name"])
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        migrations = list_applied_migrations(conn)
    finally:
        conn.close()

    assert "schema_migrations" in tables
    assert SCHEMA_BASELINE_VERSION in migrations
    assert any(c.startswith("record_migration:") for c in changes)


def test_ensure_schema_does_not_duplicate_baseline_migration(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()

    ensure_schema()
    second_changes = ensure_schema()

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT version FROM schema_migrations WHERE version = ?",
            (SCHEMA_BASELINE_VERSION,),
        ).fetchall()
    finally:
        conn.close()

    assert len(rows) == 1
    assert not any(c.startswith("record_migration:") for c in second_changes)

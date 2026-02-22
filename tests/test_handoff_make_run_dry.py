# FILE: tests/test_handoff_make_run_dry.py
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema


def test_handoff_make_run_dry_records_ok_run(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()
    ensure_schema()

    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools" / "handoff_make_run.py"
    assert script.exists()

    # subprocess inherits env (monkeypatch already set WARDROBE_DB_PATH)
    r = subprocess.run(
        [sys.executable, str(script), "--dry-run", "--base", "http://127.0.0.1:5002", "--user", "karen", "--ids", "1,2,3"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT component, op, status, summary FROM runs ORDER BY started_at DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row["component"] == "tools"
    assert row["op"] == "handoff_make"
    assert row["status"] == "ok"
    assert "dry-run" in (row["summary"] or "")
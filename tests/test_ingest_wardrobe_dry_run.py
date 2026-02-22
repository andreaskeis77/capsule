# FILE: tests/test_ingest_wardrobe_dry_run.py
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema


def test_ingest_wardrobe_dry_run_records_run(tmp_path, monkeypatch):
    # temp DB + dirs
    db_path = tmp_path / "wardrobe.db"
    img_dir = tmp_path / "images"
    input_dir = tmp_path / "01_raw_input"

    (input_dir / "karen" / "item1").mkdir(parents=True, exist_ok=True)
    (input_dir / "karen" / "item1" / "note.txt").write_text("Test item text", encoding="utf-8")
    img_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_ENV", "test")
    settings.reload_settings()
    ensure_schema()

    repo_root = Path(__file__).resolve().parents[1]

    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.ingest_wardrobe",
            "--input-dir",
            str(input_dir),
            "--archive-dir",
            str(img_dir),
            "--dry-run",
            "--max-items",
            "1",
        ],
        cwd=repo_root,
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
    assert row["component"] == "ingest"
    assert row["op"] == "wardrobe_ingest"
    assert row["status"] == "ok"
    assert "dry_run=True" in (row["summary"] or "")
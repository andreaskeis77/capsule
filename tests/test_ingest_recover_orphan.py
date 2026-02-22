from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema


def _count_items(db_path: Path) -> int:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM items")
    n = int(cur.fetchone()[0])
    conn.close()
    return n


def test_recover_orphan_archive_folder_creates_db_row(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    img_dir = tmp_path / "images"

    # create orphan archive folder
    (img_dir / "karen" / "orphan1").mkdir(parents=True, exist_ok=True)
    (img_dir / "karen" / "orphan1" / "note.txt").write_text("x", encoding="utf-8")

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_ENV", "test")
    settings.reload_settings()
    ensure_schema()

    repo_root = Path(__file__).resolve().parents[1]
    tool = repo_root / "tools" / "ingest_recover.py"
    assert tool.exists()

    r = subprocess.run(
        [sys.executable, str(tool), "--archive-dir", str(img_dir), "--user", "karen"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)

    assert _count_items(db_path) == 1
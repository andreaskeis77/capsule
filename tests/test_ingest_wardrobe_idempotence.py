# FILE: tests/test_ingest_wardrobe_idempotence.py
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


def _get_first_item(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id, image_path, ingest_status, source_fingerprint FROM items ORDER BY id ASC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row


def test_ingest_idempotence_duplicate_goes_to_quarantine(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    img_dir = tmp_path / "images"
    input_dir = tmp_path / "01_raw_input"
    quarantine_dir = tmp_path / "quarantine"

    # item1
    (input_dir / "karen" / "item1").mkdir(parents=True, exist_ok=True)
    (input_dir / "karen" / "item1" / "note.txt").write_text("SAME", encoding="utf-8")

    img_dir.mkdir(parents=True, exist_ok=True)
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_IMG_DIR", str(img_dir))
    monkeypatch.setenv("WARDROBE_ENV", "test")
    settings.reload_settings()
    ensure_schema()

    repo_root = Path(__file__).resolve().parents[1]

    # First ingest (fake-ai => no OpenAI)
    r1 = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.ingest_wardrobe",
            "--input-dir",
            str(input_dir),
            "--archive-dir",
            str(img_dir),
            "--quarantine-dir",
            str(quarantine_dir),
            "--user",
            "karen",
            "--fake-ai",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert r1.returncode == 0, (r1.stdout, r1.stderr)

    assert (img_dir / "karen" / "item1").exists()
    assert not (input_dir / "karen" / "item1").exists()

    assert _count_items(db_path) == 1
    row = _get_first_item(db_path)
    assert row["user_id"] == "karen"
    assert row["image_path"] == "karen/item1"
    assert (row["ingest_status"] or "").lower() == "ok"
    assert row["source_fingerprint"]

    # Create duplicate with different folder name but same signature
    (input_dir / "karen" / "item2").mkdir(parents=True, exist_ok=True)
    (input_dir / "karen" / "item2" / "note.txt").write_text("SAME", encoding="utf-8")

    r2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.ingest_wardrobe",
            "--input-dir",
            str(input_dir),
            "--archive-dir",
            str(img_dir),
            "--quarantine-dir",
            str(quarantine_dir),
            "--user",
            "karen",
            "--fake-ai",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0, (r2.stdout, r2.stderr)

    # duplicate should be moved out of input
    assert not (input_dir / "karen" / "item2").exists()

    # quarantine contains something for karen
    qk = quarantine_dir / "karen"
    assert qk.exists()
    assert any(p.is_dir() and p.name.startswith("item2__dup__") for p in qk.iterdir())

    # still only one item in DB
    assert _count_items(db_path) == 1
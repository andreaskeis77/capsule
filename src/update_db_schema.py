# FILE: update_db_schema.py
import os
import sqlite3
from pathlib import Path

DEFAULT_DB = Path("03_database") / "wardrobe.db"

def _db_path() -> Path:
    env = os.environ.get("WARDROBE_DB_PATH", "").strip()
    return Path(env) if env else DEFAULT_DB

def _has_column(cursor: sqlite3.Cursor, table: str, col: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor.fetchall()]
    return col in cols

def _add_column(cursor: sqlite3.Cursor, table: str, col_sql: str) -> None:
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_sql}")

def update_schema() -> None:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    if cur.fetchone() is None:
        raise RuntimeError(f"Table 'items' not found in DB: {db_path}")

    changes = []

    if not _has_column(cur, "items", "color_variant"):
        _add_column(cur, "items", "color_variant TEXT")
        changes.append("items.color_variant")
        print("[+] Added column: items.color_variant")

    if not _has_column(cur, "items", "needs_review"):
        _add_column(cur, "items", "needs_review INTEGER DEFAULT 0")
        changes.append("items.needs_review")
        print("[+] Added column: items.needs_review")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_needs_review ON items(needs_review)")
    print("[+] Ensured index: idx_items_needs_review")

    conn.commit()
    conn.close()

    if changes:
        print(f"[OK] Schema updated in {db_path}. Changes: {', '.join(changes)}")
    else:
        print(f"[OK] Schema already up to date in {db_path}.")

if __name__ == "__main__":
    update_schema()

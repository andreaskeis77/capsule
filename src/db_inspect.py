from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List

from src.db_sqlite import connect_sqlite


def fetch_inventory_rows(db_path: Path | str) -> List[sqlite3.Row]:
    conn = connect_sqlite(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM items ORDER BY id")
        return cur.fetchall()
    finally:
        conn.close()


def coerce_row(row: sqlite3.Row) -> Dict[str, object]:
    return {k: ("---" if v is None else v) for k, v in dict(row).items()}


def summarize_row(row: sqlite3.Row) -> Dict[str, object]:
    item = coerce_row(row)
    return {
        "id": item.get("id", "---"),
        "name": item.get("name", "---"),
        "brand": item.get("brand", "---"),
        "category": item.get("category", "---"),
        "color_primary": item.get("color_primary", "---"),
        "material_main": item.get("material_main", "---"),
        "fit": item.get("fit", "---"),
        "collar": item.get("collar", "---"),
        "vision_description": item.get("vision_description", "---"),
    }

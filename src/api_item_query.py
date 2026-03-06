from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional


def fetch_item_row_by_id(conn: sqlite3.Connection, item_id: int) -> Optional[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    return cur.fetchone()


def fetch_item_image_ref_by_id(conn: sqlite3.Connection, item_id: int) -> Optional[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT id, image_path FROM items WHERE id = ?", (item_id,))
    return cur.fetchone()


def list_item_summary_rows(conn: sqlite3.Connection, user_id: str) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, category, color_primary, color_variant, needs_review, context
        FROM items
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    return list(cur.fetchall())


def count_review_rows(conn: sqlite3.Connection, user_id: str) -> int:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM items WHERE user_id = ? AND needs_review = 1", (user_id,))
    row = cur.fetchone()
    if row is None:
        return 0
    return int(row["cnt"])


def list_review_rows(conn: sqlite3.Connection, user_id: str, limit: int, offset: int) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, category, color_primary, color_variant, needs_review
        FROM items
        WHERE user_id = ? AND needs_review = 1
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    )
    return list(cur.fetchall())


def item_row_to_payload(row: sqlite3.Row, base_url: str) -> Dict[str, Any]:
    image_path = row["image_path"] if "image_path" in row.keys() else None
    urls: List[str] = []
    main_url = None
    if image_path:
        main_url = f"{base_url}/images/{image_path}/main.jpg"
        urls = [main_url]
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "brand": row["brand"],
        "category": row["category"],
        "color_primary": row["color_primary"],
        "color_variant": row["color_variant"] if "color_variant" in row.keys() else None,
        "needs_review": int(row["needs_review"]) if "needs_review" in row.keys() and row["needs_review"] is not None else 0,
        "material_main": row["material_main"],
        "fit": row["fit"],
        "collar": row["collar"],
        "price": row["price"],
        "vision_description": row["vision_description"],
        "image_path": image_path,
        "created_at": row["created_at"],
        "context": row["context"] if "context" in row.keys() else None,
        "size": row["size"] if "size" in row.keys() else None,
        "notes": row["notes"] if "notes" in row.keys() else None,
        "main_image_url": main_url,
        "image_urls": urls,
    }


def item_summary_row_to_payload(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "color_primary": row["color_primary"],
        "color_variant": row["color_variant"],
        "needs_review": int(row["needs_review"] or 0),
        "context": row["context"],
    }


def review_row_to_payload(row: sqlite3.Row, suggestions: List[str]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "color_primary": row["color_primary"],
        "color_variant": row["color_variant"],
        "needs_review": int(row["needs_review"] or 0),
        "suggestions": suggestions,
    }

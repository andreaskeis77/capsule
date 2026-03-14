from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict


def connect_db(db_path: Path | str, *, timeout: float = 5) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=timeout)
    conn.row_factory = sqlite3.Row
    return conn


def run_with_connection(db_path: Path | str, operation, *args, timeout: float = 5, **kwargs):
    conn = connect_db(db_path, timeout=timeout)
    try:
        return operation(conn, *args, **kwargs)
    finally:
        conn.close()


def get_by_fingerprint(conn: sqlite3.Connection, user: str, fp: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, ingest_status, image_path FROM items WHERE user_id = ? AND source_fingerprint = ? LIMIT 1",
        (user, fp),
    )
    return cur.fetchone()


def claim_pending(conn: sqlite3.Connection, *, user: str, item_name: str, image_path: str, fp: str, run_id: str) -> int:
    """
    Claim or reuse an item-row for this fingerprint.
    Ensures there is a DB record even if we crash mid-ingest.
    """
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO items (user_id, name, image_path, source_fingerprint, ingest_status, ingest_run_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user, item_name, image_path, fp, "pending", run_id),
        )
        conn.commit()
        return int(cur.lastrowid)
    except sqlite3.IntegrityError:
        conn.rollback()
        cur.execute(
            "SELECT id FROM items WHERE user_id = ? AND source_fingerprint = ? LIMIT 1",
            (user, fp),
        )
        row = cur.fetchone()
        if not row:
            raise
        cur.execute(
            "UPDATE items SET ingest_status = ?, ingest_run_id = ?, ingest_error = NULL WHERE id = ?",
            ("pending", run_id, int(row["id"])),
        )
        conn.commit()
        return int(row["id"])


def mark_ok(conn: sqlite3.Connection, *, item_id: int, data: Dict[str, Any], run_id: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE items
        SET name = ?,
            brand = ?,
            category = ?,
            color_primary = ?,
            material_main = ?,
            fit = ?,
            collar = ?,
            price = ?,
            vision_description = ?,
            ingest_status = ?,
            ingest_run_id = ?,
            ingest_error = NULL
        WHERE id = ?
        """,
        (
            data.get("name"),
            data.get("brand"),
            data.get("category"),
            data.get("color_primary"),
            data.get("material_main"),
            data.get("fit"),
            data.get("collar"),
            data.get("price"),
            data.get("vision_description"),
            "ok",
            run_id,
            int(item_id),
        ),
    )
    conn.commit()


def mark_failed(conn: sqlite3.Connection, *, item_id: int, err: str, run_id: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "UPDATE items SET ingest_status = ?, ingest_run_id = ?, ingest_error = ? WHERE id = ?",
        ("failed", run_id, err[:500], int(item_id)),
    )
    conn.commit()

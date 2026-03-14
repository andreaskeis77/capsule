from __future__ import annotations

import sqlite3
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema
from src.ingest_item_db import claim_pending, connect_db, get_by_fingerprint, mark_failed, mark_ok



def _prepare_db(tmp_path: Path, monkeypatch) -> Path:
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    monkeypatch.setenv("WARDROBE_ENV", "test")
    settings.reload_settings()
    ensure_schema()
    return db_path



def test_claim_pending_inserts_and_reuses_existing_fingerprint(tmp_path: Path, monkeypatch):
    db_path = _prepare_db(tmp_path, monkeypatch)

    conn = connect_db(db_path)
    try:
        first_id = claim_pending(
            conn,
            user="karen",
            item_name="item1",
            image_path="karen/item1",
            fp="fp-1",
            run_id="run-1",
        )
        second_id = claim_pending(
            conn,
            user="karen",
            item_name="item1-duplicate",
            image_path="karen/item1-duplicate",
            fp="fp-1",
            run_id="run-2",
        )

        row = conn.execute(
            "SELECT id, ingest_status, ingest_run_id, ingest_error FROM items WHERE id = ?",
            (first_id,),
        ).fetchone()
    finally:
        conn.close()

    assert second_id == first_id
    assert row is not None
    assert row["ingest_status"] == "pending"
    assert row["ingest_run_id"] == "run-2"
    assert row["ingest_error"] is None



def test_get_by_fingerprint_returns_matching_row(tmp_path: Path, monkeypatch):
    db_path = _prepare_db(tmp_path, monkeypatch)

    conn = connect_db(db_path)
    try:
        item_id = claim_pending(
            conn,
            user="andreas",
            item_name="shirt",
            image_path="andreas/shirt",
            fp="fp-lookup",
            run_id="run-lookup",
        )
        row = get_by_fingerprint(conn, "andreas", "fp-lookup")
        missing = get_by_fingerprint(conn, "andreas", "missing")
    finally:
        conn.close()

    assert row is not None
    assert int(row["id"]) == item_id
    assert row["image_path"] == "andreas/shirt"
    assert missing is None



def test_mark_ok_updates_analysis_fields_and_clears_error(tmp_path: Path, monkeypatch):
    db_path = _prepare_db(tmp_path, monkeypatch)

    conn = connect_db(db_path)
    try:
        item_id = claim_pending(
            conn,
            user="karen",
            item_name="dress",
            image_path="karen/dress",
            fp="fp-ok",
            run_id="run-pending",
        )
        conn.execute("UPDATE items SET ingest_error = ? WHERE id = ?", ("stale", item_id))
        conn.commit()

        mark_ok(
            conn,
            item_id=item_id,
            run_id="run-ok",
            data={
                "name": "Evening Dress",
                "brand": "ACME",
                "category": "cat_dress",
                "color_primary": "navy",
                "material_main": "silk",
                "fit": "tailored",
                "collar": "v-neck",
                "price": "199",
                "vision_description": "Detailed description",
            },
        )

        row = conn.execute(
            "SELECT name, brand, category, color_primary, material_main, fit, collar, price, vision_description, ingest_status, ingest_run_id, ingest_error FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row["name"] == "Evening Dress"
    assert row["brand"] == "ACME"
    assert row["category"] == "cat_dress"
    assert row["ingest_status"] == "ok"
    assert row["ingest_run_id"] == "run-ok"
    assert row["ingest_error"] is None



def test_mark_failed_sets_failed_status_and_truncates_error(tmp_path: Path, monkeypatch):
    db_path = _prepare_db(tmp_path, monkeypatch)

    conn = connect_db(db_path)
    try:
        item_id = claim_pending(
            conn,
            user="karen",
            item_name="coat",
            image_path="karen/coat",
            fp="fp-fail",
            run_id="run-start",
        )
        long_error = "x" * 800

        mark_failed(conn, item_id=item_id, err=long_error, run_id="run-failed")

        row = conn.execute(
            "SELECT ingest_status, ingest_run_id, ingest_error FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row["ingest_status"] == "failed"
    assert row["ingest_run_id"] == "run-failed"
    assert row["ingest_error"] == ("x" * 500)



def test_ingest_wardrobe_keeps_db_helper_aliases_for_stable_imports():
    from src import ingest_wardrobe
    from src.ingest_item_db import claim_pending as db_claim_pending
    from src.ingest_item_db import get_by_fingerprint as db_get_by_fingerprint
    from src.ingest_item_db import mark_failed as db_mark_failed
    from src.ingest_item_db import mark_ok as db_mark_ok

    assert ingest_wardrobe._db_claim_pending is db_claim_pending
    assert ingest_wardrobe._db_get_by_fingerprint is db_get_by_fingerprint
    assert ingest_wardrobe._db_mark_ok is db_mark_ok
    assert ingest_wardrobe._db_mark_failed is db_mark_failed

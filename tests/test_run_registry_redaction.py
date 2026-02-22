# FILE: tests/test_run_registry_redaction.py
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src import settings
from src.db_schema import ensure_schema
from src.run_registry import REDACT_PLACEHOLDER, start_run


def test_run_registry_redacts_secrets_in_meta_and_events(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()
    ensure_schema()

    meta = {
        "OPENAI_API_KEY": "sk-test-THISMUSTNOTPERSIST",
        "WARDROBE_API_KEY": "supersecret",
        "nested": {"authorization": "Bearer abc.def.ghi", "ok": "keepme"},
    }
    h = start_run("test", "redaction", meta=meta)
    h.event(
        "test.event",
        data={"token": "should_not_persist", "safe": {"x": 1}, "list": [{"access_token": "nope"}]},
    )
    h.ok(summary="done")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT meta_json FROM runs WHERE run_id = ?", (h.run_id,))
    mrow = cur.fetchone()
    assert mrow is not None
    meta_json = json.loads(mrow["meta_json"])
    assert meta_json["OPENAI_API_KEY"] == REDACT_PLACEHOLDER
    assert meta_json["WARDROBE_API_KEY"] == REDACT_PLACEHOLDER
    assert meta_json["nested"]["authorization"] == REDACT_PLACEHOLDER
    assert meta_json["nested"]["ok"] == "keepme"

    cur.execute("SELECT data_json FROM run_events WHERE run_id = ? ORDER BY id ASC LIMIT 1", (h.run_id,))
    erow = cur.fetchone()
    assert erow is not None
    data_json = json.loads(erow["data_json"])
    assert data_json["token"] == REDACT_PLACEHOLDER
    assert data_json["list"][0]["access_token"] == REDACT_PLACEHOLDER
    assert data_json["safe"]["x"] == 1

    # Ensure raw secret strings do not appear anywhere in stored JSON
    raw = (mrow["meta_json"] or "") + (erow["data_json"] or "")
    assert "sk-test-THISMUSTNOTPERSIST" not in raw
    assert "supersecret" not in raw
    assert "abc.def.ghi" not in raw

    conn.close()
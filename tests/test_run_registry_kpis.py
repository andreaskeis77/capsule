# FILE: tests/test_run_registry_kpis.py
from __future__ import annotations

from pathlib import Path

import pytest

from src import settings
from src.db_schema import ensure_schema
from src.run_registry import compute_kpis, list_runs, run_context


def test_kpis_basic(tmp_path, monkeypatch):
    db_path = tmp_path / "wardrobe.db"
    monkeypatch.setenv("WARDROBE_DB_PATH", str(db_path))
    settings.reload_settings()
    ensure_schema()

    with run_context("test", "ok_run") as r1:
        r1.event("a")

    with pytest.raises(RuntimeError):
        with run_context("test", "fail_run") as r2:
            r2.event("b")
            raise RuntimeError("boom")

    k = compute_kpis(component="test")
    assert k["total_runs"] >= 2
    assert k["counts"]["ok"] >= 1
    assert k["counts"]["failed"] >= 1
    assert k["RSR"] is not None
    assert k["FRR"] is not None

    runs = list_runs(component="test", limit=10)
    assert len(runs) >= 2
    assert any(r["op"] == "ok_run" for r in runs)
    assert any(r["op"] == "fail_run" for r in runs)
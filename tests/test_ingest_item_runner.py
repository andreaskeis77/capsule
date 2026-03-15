from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from src.ingest_item_runner import Stats, build_run_meta, resolve_requested_users, run_ingest
from src.ingest_wardrobe import Stats as ward_stats


class DummyConn:
    def close(self):
        return None


class FakeRun:
    def __init__(self):
        self.run_id = "run-1"
        self.events = []
        self.summary = None
        self.status = None

    def event(self, name, level=None, message=None, data=None):
        self.events.append({"name": name, "level": level, "message": message, "data": data})

    def ok(self, summary=None):
        self.status = "ok"
        self.summary = summary

    def fail(self, summary=None):
        self.status = "failed"
        self.summary = summary

    def partial(self, summary=None):
        self.status = "partial"
        self.summary = summary


def _args(**overrides):
    data = {
        "user": "",
        "max_items": 0,
        "dry_run": False,
        "fake_ai": False,
        "model": "gpt-4o-mini",
        "max_images": 3,
        "force": False,
    }
    data.update(overrides)
    return Namespace(**data)


def test_ingest_wardrobe_aliases_runner_stats():
    assert ward_stats is Stats


def test_build_run_meta_captures_paths_and_flags(tmp_path):
    args = _args(user="karen", max_items=2, dry_run=True, fake_ai=False, force=True)
    meta = build_run_meta(
        args,
        input_dir=tmp_path / "in",
        archive_dir=tmp_path / "archive",
        quarantine_dir=tmp_path / "quarantine",
    )

    assert meta == {
        "input_dir": str(tmp_path / "in"),
        "archive_dir": str(tmp_path / "archive"),
        "quarantine_dir": str(tmp_path / "quarantine"),
        "user": "karen",
        "max_items": 2,
        "dry_run": True,
        "fake_ai": False,
        "model": "gpt-4o-mini",
        "max_images": 3,
        "force": True,
    }


def test_resolve_requested_users_rejects_invalid_user(tmp_path):
    run = FakeRun()
    users, exit_code = resolve_requested_users(
        args_user="nope",
        input_dir=tmp_path,
        valid_users={"andreas", "karen"},
        run=run,
    )

    assert users is None
    assert exit_code == 2
    assert run.status == "failed"
    assert run.summary == "InvalidUser: nope"
    assert any(event["name"] == "ingest.invalid_user" for event in run.events)


def test_run_ingest_missing_input_returns_error(tmp_path):
    run = FakeRun()
    rc = run_ingest(
        args=_args(dry_run=True),
        run=run,
        t0=0.0,
        now_s=lambda: 1.0,
        input_dir=tmp_path / "missing",
        archive_dir=tmp_path / "archive",
        quarantine_dir=tmp_path / "quarantine",
        valid_users={"andreas", "karen"},
        connect_ro=lambda: DummyConn(),
        write_connection=lambda *a, **k: None,
        list_image_files=lambda _: [],
        read_text_files=lambda _: "",
        folder_signature_fingerprint=lambda _: "fp",
        db_get_by_fingerprint=lambda conn, user, fp: None,
        db_claim_pending=lambda *a, **k: 1,
        db_mark_ok=lambda *a, **k: None,
        db_mark_failed=lambda *a, **k: None,
        robust_move=lambda src, dst: True,
        analyze_item_hybrid=lambda *a, **k: None,
        fake_ai=lambda *a, **k: {},
    )

    assert rc == 2
    assert run.status == "failed"
    assert "MissingInputDir" in (run.summary or "")
    assert any(event["name"] == "ingest.input_missing" for event in run.events)


def test_run_ingest_dry_run_processes_item(tmp_path):
    input_dir = tmp_path / "input"
    archive_dir = tmp_path / "archive"
    quarantine_dir = tmp_path / "quarantine"
    item_dir = input_dir / "karen" / "item1"
    item_dir.mkdir(parents=True)
    (item_dir / "note.txt").write_text("hello", encoding="utf-8")

    run = FakeRun()
    rc = run_ingest(
        args=_args(dry_run=True),
        run=run,
        t0=0.0,
        now_s=lambda: 1.25,
        input_dir=input_dir,
        archive_dir=archive_dir,
        quarantine_dir=quarantine_dir,
        valid_users={"andreas", "karen"},
        connect_ro=lambda: DummyConn(),
        write_connection=lambda *a, **k: None,
        list_image_files=lambda path: [],
        read_text_files=lambda path: "hello",
        folder_signature_fingerprint=lambda path: "abc123456789",
        db_get_by_fingerprint=lambda conn, user, fp: None,
        db_claim_pending=lambda *a, **k: 1,
        db_mark_ok=lambda *a, **k: None,
        db_mark_failed=lambda *a, **k: None,
        robust_move=lambda src, dst: True,
        analyze_item_hybrid=lambda *a, **k: None,
        fake_ai=lambda *a, **k: {},
    )

    assert rc == 0
    assert run.status == "ok"
    assert "dry_run=True" in (run.summary or "")
    assert any(event["name"] == "item.dry_run" for event in run.events)

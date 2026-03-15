from __future__ import annotations

import logging
from pathlib import Path

from src.ingest_item_fs import robust_move, robust_rmtree
from src.ingest_wardrobe import _robust_rmtree as ward_robust_rmtree, robust_move as ward_robust_move


def test_robust_rmtree_missing_path_noop(tmp_path):
    missing = tmp_path / "missing"
    robust_rmtree(missing)
    assert not missing.exists()


def test_robust_move_replaces_existing_destination(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "nested").mkdir(parents=True)
    (src / "nested" / "data.txt").write_text("payload", encoding="utf-8")
    dst.mkdir()
    (dst / "old.txt").write_text("old", encoding="utf-8")

    ok = robust_move(src, dst)

    assert ok is True
    assert not src.exists()
    assert (dst / "nested" / "data.txt").read_text(encoding="utf-8") == "payload"
    assert not (dst / "old.txt").exists()


def test_robust_move_retries_permission_error_then_succeeds(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "file.txt").write_text("x", encoding="utf-8")

    calls = {"n": 0}
    sleeps = []

    def fake_move(src_arg: str, dst_arg: str):
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError("locked")
        Path(dst_arg).parent.mkdir(parents=True, exist_ok=True)
        Path(src_arg).rename(dst_arg)

    ok = robust_move(src, dst, move_func=fake_move, sleep_func=sleeps.append)

    assert ok is True
    assert calls["n"] == 2
    assert sleeps == [0.8]
    assert dst.exists()
    assert not src.exists()


def test_robust_move_returns_false_on_generic_exception(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()

    def boom(src_arg: str, dst_arg: str):
        raise RuntimeError("boom")

    ok = robust_move(src, dst, move_func=boom, sleep_func=lambda _: None)

    assert ok is False
    assert src.exists()
    assert not dst.exists()


def test_ingest_wardrobe_aliases_fs_helpers():
    assert ward_robust_rmtree is robust_rmtree
    assert ward_robust_move is robust_move

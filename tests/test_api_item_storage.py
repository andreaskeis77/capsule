from __future__ import annotations

from pathlib import Path

from src.api_item_storage import (
    cleanup_trashed_image_dir,
    create_image_folder_for_item,
    item_rel_dir,
    move_image_folder_for_item,
    move_item_image_dir_to_trash,
    rollback_moved_image_dir,
    rollback_trashed_image_dir,
)


def test_item_rel_dir_slugifies_and_builds_user_root():
    rel = item_rel_dir("karen", "Roter Blazer", 7)
    assert rel == "karen/roter-blazer_7"


def test_create_move_and_rollback_folder(tmp_path: Path):
    base = tmp_path / "images"
    base.mkdir()

    created = create_image_folder_for_item(base, "karen", "Roter Blazer", 7, b"jpg")
    assert created.rel_path == "karen/roter-blazer_7"
    assert created.main_path.exists()

    move_result = move_image_folder_for_item(base, created.rel_path, "andreas", "Blauer Blazer", 7)
    assert move_result.moved is True
    assert move_result.new_rel == "andreas/blauer-blazer_7"
    assert move_result.dst_dir.exists()
    assert not move_result.src_dir.exists()

    rollback_moved_image_dir(move_result)
    assert move_result.src_dir.exists()
    assert not move_result.dst_dir.exists()


def test_move_to_trash_and_cleanup(tmp_path: Path):
    base = tmp_path / "images"
    trash = tmp_path / "trash"
    base.mkdir()
    trash.mkdir()

    created = create_image_folder_for_item(base, "karen", "Roter Blazer", 7, b"jpg")
    trash_result = move_item_image_dir_to_trash(base, trash, created.rel_path, 7, "req-123456")

    assert trash_result.moved is True
    assert not trash_result.src_dir.exists()
    assert trash_result.trash_dir.exists()

    rollback_trashed_image_dir(trash_result)
    assert trash_result.src_dir.exists()
    assert not trash_result.trash_dir.exists()

    trash_result = move_item_image_dir_to_trash(base, trash, created.rel_path, 7, "req-123456")
    cleanup_trashed_image_dir(trash_result)
    assert not trash_result.trash_dir.exists()
    assert not trash_result.src_dir.exists()

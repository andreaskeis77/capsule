from __future__ import annotations

from pathlib import Path

from src.ingest_item_io import (
    VALID_IMAGE_EXTS,
    VALID_TEXT_EXTS,
    encode_bytes,
    folder_signature_fingerprint,
    image_to_data_url,
    list_image_files,
    read_text_files,
)


def test_read_text_files_collects_recursive_txt_content(tmp_path: Path):
    item_dir = tmp_path / "item"
    (item_dir / "sub").mkdir(parents=True)
    (item_dir / "a.txt").write_text("alpha", encoding="utf-8")
    (item_dir / "sub" / "b.txt").write_text("beta", encoding="utf-8")
    (item_dir / "ignore.md").write_text("gamma", encoding="utf-8")

    content = read_text_files(item_dir)

    assert content == "alpha\nbeta"
    assert VALID_TEXT_EXTS == {".txt"}


def test_list_image_files_filters_and_sorts_supported_extensions(tmp_path: Path):
    item_dir = tmp_path / "item"
    (item_dir / "sub").mkdir(parents=True)
    (item_dir / "b.png").write_bytes(b"png")
    (item_dir / "sub" / "a.JPG").write_bytes(b"jpg")
    (item_dir / "skip.txt").write_text("nope", encoding="utf-8")

    images = list_image_files(item_dir)

    assert [p.relative_to(item_dir).as_posix() for p in images] == ["b.png", "sub/a.JPG"]
    assert ".jpg" in VALID_IMAGE_EXTS


def test_folder_signature_fingerprint_is_stable_across_outer_folder_rename(tmp_path: Path):
    item_a = tmp_path / "outer_a"
    item_b = tmp_path / "outer_b"
    (item_a / "nested").mkdir(parents=True)
    (item_b / "nested").mkdir(parents=True)
    (item_a / "nested" / "note.txt").write_text("same", encoding="utf-8")
    (item_b / "nested" / "note.txt").write_text("same", encoding="utf-8")

    assert folder_signature_fingerprint(item_a) == folder_signature_fingerprint(item_b)


def test_image_to_data_url_reads_supported_binary_image_without_reencoding(tmp_path: Path):
    path = tmp_path / "sample.jfif"
    path.write_bytes(b"fake-image-bytes")

    payload = image_to_data_url(path)

    assert payload is not None
    assert payload["type"] == "image_url"
    assert payload["image_url"]["url"] == f"data:image/jpeg;base64,{encode_bytes(b'fake-image-bytes')}"


def test_image_to_data_url_returns_none_for_missing_or_unsupported_file(tmp_path: Path):
    missing = tmp_path / "missing.heic"

    assert image_to_data_url(missing) is None


def test_ingest_wardrobe_keeps_helper_aliases_for_stable_imports():
    from src import ingest_wardrobe

    assert ingest_wardrobe._read_text_files is read_text_files
    assert ingest_wardrobe._list_image_files is list_image_files
    assert ingest_wardrobe._folder_signature_fingerprint is folder_signature_fingerprint
    assert ingest_wardrobe._image_to_data_url is image_to_data_url
    assert ingest_wardrobe._encode_bytes is encode_bytes

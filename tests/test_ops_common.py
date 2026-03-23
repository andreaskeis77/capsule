from __future__ import annotations

from pathlib import Path

from tools.ops_common import read_text_robust, run_command, sha256_file, truncate_text, write_json, write_text


def test_write_text_and_json_create_parent_dirs(tmp_path):
    text_path = tmp_path / "a" / "b" / "c.txt"
    json_path = tmp_path / "x" / "y" / "payload.json"

    write_text(text_path, "hello")
    write_json(json_path, {"ok": True})

    assert text_path.read_text(encoding="utf-8") == "hello"
    assert '"ok": true' in json_path.read_text(encoding="utf-8").lower()


def test_read_text_robust_handles_utf8_sig(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfHello")
    assert read_text_robust(path) == "Hello"


def test_sha256_file_is_stable(tmp_path):
    path = tmp_path / "f.txt"
    path.write_text("abc", encoding="utf-8")
    assert sha256_file(path) == sha256_file(path)


def test_run_command_captures_stdout(tmp_path):
    rc, out = run_command(["python", "-c", "print('ok')"], cwd=tmp_path)
    assert rc == 0
    assert "ok" in out


def test_truncate_text_shortens_long_values():
    assert truncate_text("abcdef", 5) == "ab..."

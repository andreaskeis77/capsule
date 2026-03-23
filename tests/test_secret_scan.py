# FILE: tests/test_secret_scan.py
from __future__ import annotations

from pathlib import Path

from tools.secret_scan import REPO_ROOT, scan_paths, scan_text


def test_detects_openai_key(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("OPENAI_API_KEY=sk-test-THISMUSTNOTPERSIST1234567890\n", encoding="utf-8")  # secret-scan:ignore
    findings = scan_paths([p], repo_root=Path(REPO_ROOT), max_bytes=2_000_000)
    assert any(f.kind in {"openai_key", "sensitive_assignment"} for f in findings)


def test_ignore_marker_suppresses(tmp_path):
    p = tmp_path / "b.txt"
    p.write_text(
        "OPENAI_API_KEY=sk-test-THISMUSTNOTPERSIST1234567890 # secret-scan:ignore\n",
        encoding="utf-8",
    )
    findings = scan_paths([p], repo_root=Path(REPO_ROOT), max_bytes=2_000_000)
    assert not any(f.kind in {"openai_key", "sensitive_assignment"} for f in findings)


def test_detects_private_key_block(tmp_path):
    p = tmp_path / "c.pem"
    p.write_text("-----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----\n", encoding="utf-8")  # secret-scan:ignore
    findings = scan_paths([p], repo_root=Path(REPO_ROOT), max_bytes=2_000_000)
    assert any(f.kind == "private_key_block" for f in findings)


def test_detects_long_api_key_assignment(tmp_path):
    p = tmp_path / "d.env"
    p.write_text("WARDROBE_API_KEY=THISMUSTNOTPERSIST-1234567890-ABCDEFGHIJKLMNOPQRSTUVWXYZ\n", encoding="utf-8")  # secret-scan:ignore
    findings = scan_paths([p], repo_root=Path(REPO_ROOT), max_bytes=2_000_000)
    assert any(f.kind == "sensitive_assignment" for f in findings)


def test_python_expression_with_sensitive_name_is_not_flagged():
    findings = scan_text('x_api_key = Header(None, alias="X-API-Key")\n', 'src/api_v2.py')
    assert findings == []


def test_python_expression_with_token_variables_is_not_flagged():
    findings = scan_text(
        'tokens = _tokenize(value)\nnormalized_token = token.strip().lower()\n',
        'src/ontology_runtime_index.py',
    )
    assert findings == []

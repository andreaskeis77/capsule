from __future__ import annotations

from pathlib import Path

from tools.reporting_common import render_table, to_repo_rel, write_json


def test_to_repo_rel_normalizes_windows_style_separators(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "docs" / "_ops" / "quality_gates" / "run_1" / "summary.json"
    nested.parent.mkdir(parents=True)
    nested.write_text("{}", encoding="utf-8")
    rel = to_repo_rel(nested, repo)
    assert rel == "docs/_ops/quality_gates/run_1/summary.json"


def test_render_table_builds_markdown_rows():
    rows = render_table(["a", "b"], [[1, 2], [3, 4]])
    assert rows[0] == "| a | b |"
    assert rows[1] == "| --- | --- |"
    assert rows[2] == "| 1 | 2 |"


def test_write_json_serializes_with_terminal_newline(tmp_path):
    out = tmp_path / "out.json"
    write_json(out, {"a": 1})
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '"a": 1' in text

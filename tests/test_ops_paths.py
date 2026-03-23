from __future__ import annotations

from pathlib import Path

from tools.ops_paths import bootstrap_repo_root, find_repo_root, repo_relative


def test_find_repo_root_from_nested_script(tmp_path):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    script = root / "tools" / "demo.py"
    script.parent.mkdir(parents=True)
    script.write_text("print('x')", encoding="utf-8")

    assert find_repo_root(script) == root


def test_repo_relative_uses_forward_slashes(tmp_path):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    file_path = root / "tools" / "nested" / "x.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("x=1", encoding="utf-8")

    assert repo_relative(file_path, repo_root=root) == "tools/nested/x.py"


def test_bootstrap_repo_root_returns_root(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    script = root / "tools" / "runner.py"
    script.parent.mkdir(parents=True)
    script.write_text("print('x')", encoding="utf-8")

    monkeypatch.syspath_prepend(str(root / "tools"))
    resolved = bootstrap_repo_root(script)
    assert resolved == root

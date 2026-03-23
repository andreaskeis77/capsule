#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


def find_repo_root(start: str | Path) -> Path:
    cur = Path(start).resolve()
    if cur.is_file():
        cur = cur.parent
    for _ in range(25):
        if (cur / ".git").exists() or (cur / "src").exists() or (cur / "tools").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path(start).resolve().parent if Path(start).resolve().is_file() else Path(start).resolve()


def bootstrap_repo_root(script_file: str | Path, *, prepend: bool = True) -> Path:
    root = find_repo_root(script_file)
    root_str = str(root)
    if root_str not in sys.path:
        if prepend:
            sys.path.insert(0, root_str)
        else:
            sys.path.append(root_str)
    return root


def repo_relative(path: str | Path, *, repo_root: str | Path | None = None) -> str:
    p = Path(path).resolve()
    root = Path(repo_root).resolve() if repo_root is not None else find_repo_root(p)
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

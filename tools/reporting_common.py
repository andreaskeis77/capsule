from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def to_repo_rel(path: str | Path, repo_root: str | Path) -> str:
    p = Path(path).resolve()
    root = Path(repo_root).resolve()
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _normalize(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(v) for v in value]
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def write_json(path: str | Path, payload: Any) -> Path:
    p = ensure_parent(path)
    p.write_text(json.dumps(_normalize(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def write_markdown(path: str | Path, lines: Sequence[str]) -> Path:
    p = ensure_parent(path)
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def render_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return out

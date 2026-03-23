#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

try:
    from tools.ops_paths import ensure_dir, find_repo_root, repo_relative
except Exception:  # pragma: no cover - direct script execution fallback
    from ops_paths import ensure_dir, find_repo_root, repo_relative  # type: ignore


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_text(path: str | Path, text: str) -> Path:
    p = ensure_parent(path)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def write_json(path: str | Path, payload: Any) -> Path:
    p = ensure_parent(path)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return p


def copy_if_exists(src: str | Path, dst: str | Path) -> bool:
    src_p = Path(src)
    if not src_p.exists():
        return False
    dst_p = ensure_parent(dst)
    dst_p.write_bytes(src_p.read_bytes())
    return True


def run_command(cmd: Sequence[str], *, cwd: str | Path, timeout: int | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(Path(cwd)),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return int(proc.returncode), out.strip()
    except Exception as exc:
        return 999, f"ERROR running {list(cmd)}: {exc}"


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text_robust(path: str | Path) -> str:
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def truncate_text(value: str | None, max_chars: int = 4000) -> str:
    if not value:
        return ""
    return value if len(value) <= max_chars else value[: max_chars - 3] + "..."


def fmt_bytes(n: int) -> str:
    value = float(n)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024:
            return f"{value:.0f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    header = "| " + " | ".join(headers) + " |\n"
    sep = "|" + "|".join("---" for _ in headers) + "|\n"
    body = "".join("| " + " | ".join(str(cell) for cell in row) + " |\n" for row in rows)
    return header + sep + body

#!/usr/bin/env python3
"""
Wardrobe Studio - Project Audit Dump
Creates a deterministic, comprehensive snapshot of the repository:
- repo metadata (python version, platform, time)
- git info (if available)
- tree of files and directories
- per-file metadata (size, mtime, sha256)
- full contents for text files (with safe redaction)
- binary files: metadata only by default (optional base64)
- ignores noisy/large dirs by default (.venv, __pycache__, logs, images, db, node_modules, etc.)
  You can override with flags.

Design goals (Engineering Manifest):
- reproducibility, observability, safe defaults (no secrets in logs), deterministic ordering
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import fnmatch
import hashlib
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


# ---------------------------
# Defaults / Policy
# ---------------------------

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "logs",
    "02_wardrobe_images",
    "03_database",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}

DEFAULT_EXCLUDE_GLOBS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.dll",
    "*.exe",
    "*.so",
    "*.dylib",
    "*.zip",
    "*.7z",
    "*.rar",
    "*.tar",
    "*.gz",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.webp",
    "*.mp4",
    "*.mov",
    "*.avi",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
]

# Files that often contain secrets or sensitive data
SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.prod",
    ".env.production",
}

# Simple redaction patterns (best-effort)
REDACT_PATTERNS = [
    # KEY=... patterns (common env style)
    (re.compile(r"(?im)^(.*?(api[_-]?key|secret|token|password|pwd)\s*=\s*)(.+)$"), r"\1<REDACTED>"),
    # JSON-ish: "api_key": "..."
    (re.compile(r'(?i)("?(api[_-]?key|secret|token|password)"?\s*:\s*")([^"]+)(")'), r'\1<REDACTED>\4'),
]


@dataclass
class FileRecord:
    rel_path: str
    size: int
    mtime_iso: str
    sha256: str
    is_binary: bool
    included_content: bool
    notes: str = ""


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_probably_binary(data: bytes) -> bool:
    if not data:
        return False
    # Heuristic: NUL byte suggests binary
    if b"\x00" in data:
        return True
    # If many non-text bytes, treat as binary
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    nontext = data.translate(None, text_chars)
    return len(nontext) / max(1, len(data)) > 0.30


def safe_read_text(path: Path, max_bytes: int) -> Tuple[str, str]:
    """
    Read up to max_bytes and decode robustly.
    Returns (text, note).
    """
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
        note = f"TRUNCATED to {max_bytes} bytes"
    else:
        note = ""

    # try utf-8 first, fallback to cp1252 (common on Windows) then latin-1
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), note
        except UnicodeDecodeError:
            continue
    # last resort
    return raw.decode("latin-1", errors="replace"), (note + " (decoded with latin-1 errors=replace)").strip()


def redact_secrets(text: str) -> str:
    out = text
    for pat, repl in REDACT_PATTERNS:
        out = pat.sub(repl, out)
    return out


def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
        out = (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")
        return r.returncode, out.strip()
    except Exception as e:
        return 999, f"ERROR running {cmd}: {e}"


def git_info(repo_root: Path) -> str:
    code, out = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], repo_root)
    if code != 0 or "true" not in out.lower():
        return "_git: not available_\n"

    parts = []
    for title, cmd in [
        ("git status", ["git", "status", "--porcelain=v1"]),
        ("git branch", ["git", "branch", "--show-current"]),
        ("git head", ["git", "rev-parse", "HEAD"]),
        ("git log (last 10)", ["git", "log", "--oneline", "-n", "10"]),
    ]:
        _, o = run_cmd(cmd, repo_root)
        parts.append(f"### {title}\n```\n{o or '(no output)'}\n```\n")
    return "\n".join(parts)


def should_exclude(path: Path, rel: str, exclude_dirs: set[str], exclude_globs: List[str]) -> bool:
    # Exclude by directory name
    parts = set(Path(rel).parts)
    if parts & exclude_dirs:
        return True

    # Exclude by glob patterns
    for g in exclude_globs:
        if fnmatch.fnmatch(Path(rel).name, g) or fnmatch.fnmatch(rel.replace("\\", "/"), g):
            return True

    return False


def iter_files(repo_root: Path, use_git_ls: bool) -> List[Path]:
    """
    Deterministic list of files.
    - prefer git ls-files when possible (only tracked files)
    - fallback to full walk
    """
    if use_git_ls:
        code, out = run_cmd(["git", "ls-files"], repo_root)
        if code == 0 and out.strip():
            files = [repo_root / line.strip() for line in out.splitlines() if line.strip()]
            return sorted(files, key=lambda p: str(p).lower())
    # fallback: full walk
    files: List[Path] = []
    for root, _, filenames in os.walk(repo_root):
        for fn in filenames:
            files.append(Path(root) / fn)
    return sorted(files, key=lambda p: str(p).lower())


def tree_view(paths: List[str]) -> str:
    """
    Simple tree view from list of relative file paths.
    """
    # Build nested dict
    tree: dict = {}
    for p in paths:
        cur = tree
        parts = Path(p).parts
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur.setdefault(parts[-1], None)

    def render(node: dict, prefix: str = "") -> List[str]:
        lines: List[str] = []
        keys = sorted(node.keys(), key=lambda s: s.lower())
        for i, k in enumerate(keys):
            last = (i == len(keys) - 1)
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + k)
            child = node[k]
            if isinstance(child, dict):
                extension = "    " if last else "│   "
                lines.extend(render(child, prefix + extension))
        return lines

    return "\n".join(render(tree))


def dump_project(
    repo_root: Path,
    out_path: Path,
    max_bytes: int,
    include_binary: bool,
    include_untracked: bool,
    include_sensitive_fulltext: bool,
    exclude_dirs: set[str],
    exclude_globs: List[str],
) -> int:
    errors: List[str] = []
    records: List[FileRecord] = []

    use_git_ls = not include_untracked
    files = iter_files(repo_root, use_git_ls=use_git_ls)

    # Compute filtered rel paths
    included_files: List[Path] = []
    rels: List[str] = []
    for f in files:
        try:
            rel = str(f.relative_to(repo_root)).replace("\\", "/")
        except Exception:
            continue
        if should_exclude(f, rel, exclude_dirs, exclude_globs):
            continue
        included_files.append(f)
        rels.append(rel)

    header = []
    header.append("# Wardrobe Studio – Project Audit Dump\n")
    header.append(f"- generated_utc: {utc_now_iso()}\n")
    header.append(f"- repo_root: {repo_root}\n")
    header.append(f"- python: {sys.version.split()[0]}\n")
    header.append(f"- platform: {platform.platform()}\n")
    header.append(f"- file_mode: {'git ls-files (tracked only)' if use_git_ls else 'os.walk (tracked + untracked)'}\n")
    header.append(f"- max_bytes_per_file: {max_bytes}\n")
    header.append(f"- include_binary_base64: {include_binary}\n")
    header.append(f"- include_sensitive_fulltext: {include_sensitive_fulltext}\n")
    header.append("\n---\n")

    # Git info
    header.append("## Git Info\n\n")
    header.append(git_info(repo_root))
    header.append("\n---\n")

    # Tree
    header.append("## Project Tree (filtered)\n\n")
    header.append("```\n")
    header.append(tree_view(rels) if rels else "(no files)\n")
    header.append("\n```\n")
    header.append("\n---\n")

    # Write progressively (streaming)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        out.write("".join(header))

        out.write("## File Index\n\n")
        out.write("| # | path | size | mtime_utc | sha256 | binary | content |\n")
        out.write("|---:|---|---:|---|---|:---:|:---:|\n")

        # First pass: metadata
        for idx, f in enumerate(included_files, start=1):
            rel = str(f.relative_to(repo_root)).replace("\\", "/")
            try:
                st = f.stat()
                size = int(st.st_size)
                mtime = dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).replace(microsecond=0).isoformat()
                digest = sha256_file(f)

                # decide binary/text
                sample = f.read_bytes()[:4096]
                binary = is_probably_binary(sample)

                # by default: include full content for text files
                include_content = (not binary) or include_binary
                notes = ""

                # safety: sensitive files redacted by default; fulltext only if explicitly allowed
                if f.name in SENSITIVE_FILES and not include_sensitive_fulltext:
                    include_content = False
                    notes = "sensitive_file: content omitted (metadata only)"

                rec = FileRecord(rel, size, mtime, digest, binary, include_content, notes)
                records.append(rec)

                out.write(
                    f"| {idx} | `{rec.rel_path}` | {rec.size} | {rec.mtime_iso} | `{rec.sha256}` | "
                    f"{'yes' if rec.is_binary else 'no'} | {'yes' if rec.included_content else 'no'} |\n"
                )
            except Exception as e:
                errors.append(f"[INDEX] {rel}: {e}")

        out.write("\n---\n")

        # Second pass: contents
        out.write("## File Contents\n\n")

        for rec in records:
            out.write(f"### `{rec.rel_path}`\n\n")
            out.write(f"- size: {rec.size}\n")
            out.write(f"- mtime_utc: {rec.mtime_iso}\n")
            out.write(f"- sha256: `{rec.sha256}`\n")
            out.write(f"- binary: {'yes' if rec.is_binary else 'no'}\n")
            if rec.notes:
                out.write(f"- notes: {rec.notes}\n")
            out.write("\n")

            f = repo_root / rec.rel_path
            if not rec.included_content:
                out.write("_content omitted_\n\n---\n\n")
                continue

            try:
                if rec.is_binary and include_binary:
                    raw = f.read_bytes()
                    if len(raw) > max_bytes:
                        raw = raw[:max_bytes]
                        out.write(f"_binary content truncated to {max_bytes} bytes_\n\n")
                    b64 = base64.b64encode(raw).decode("ascii")
                    out.write("```base64\n")
                    out.write(b64)
                    out.write("\n```\n\n---\n\n")
                else:
                    text, note = safe_read_text(f, max_bytes=max_bytes)
                    text = redact_secrets(text)
                    if note:
                        out.write(f"_note: {note}_\n\n")
                    out.write("```text\n")
                    out.write(text.rstrip("\n"))
                    out.write("\n```\n\n---\n\n")
            except Exception as e:
                errors.append(f"[CONTENT] {rec.rel_path}: {e}")
                out.write(f"_ERROR reading file content: {e}_\n\n---\n\n")

        # Footer summary
        out.write("## Summary\n\n")
        out.write(f"- files_included: {len(records)}\n")
        out.write(f"- errors: {len(errors)}\n")
        if errors:
            out.write("\n### Errors\n\n")
            out.write("```\n")
            out.write("\n".join(errors))
            out.write("\n```\n")

    return 0 if not errors else 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a deterministic full project audit dump (tree + file contents).")
    p.add_argument("--root", default=".", help="Repo root (default: current directory).")
    p.add_argument("--out", required=True, help="Output file path (e.g., docs/_snapshot/project_audit_dump.md)")
    p.add_argument("--max-bytes", type=int, default=1_000_000, help="Max bytes per file to include (default: 1,000,000).")
    p.add_argument("--include-binary", action="store_true", help="Include binary files as base64 (default: off).")
    p.add_argument("--include-untracked", action="store_true", help="Include untracked files (os.walk) instead of git ls-files.")
    p.add_argument("--include-sensitive-fulltext", action="store_true",
                   help="Include full content of sensitive files like .env (DANGEROUS). Default: off.")
    p.add_argument("--no-default-excludes", action="store_true", help="Do not apply default exclude dirs/globs.")
    p.add_argument("--exclude-dir", action="append", default=[], help="Additional dir name to exclude (repeatable).")
    p.add_argument("--exclude-glob", action="append", default=[], help="Additional glob to exclude (repeatable).")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.root).resolve()
    out_path = Path(args.out).resolve()

    if not repo_root.exists():
        print(f"ERROR: root does not exist: {repo_root}", file=sys.stderr)
        return 2

    exclude_dirs = set()
    exclude_globs: List[str] = []
    if not args.no_default_excludes:
        exclude_dirs |= DEFAULT_EXCLUDE_DIRS
        exclude_globs += DEFAULT_EXCLUDE_GLOBS

    exclude_dirs |= set(args.exclude_dir or [])
    exclude_globs += (args.exclude_glob or [])

    rc = dump_project(
        repo_root=repo_root,
        out_path=out_path,
        max_bytes=args.max_bytes,
        include_binary=bool(args.include_binary),
        include_untracked=bool(args.include_untracked),
        include_sensitive_fulltext=bool(args.include_sensitive_fulltext),
        exclude_dirs=exclude_dirs,
        exclude_globs=exclude_globs,
    )

    print(f"Audit dump written to: {out_path}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
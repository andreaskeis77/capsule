#!/usr/bin/env python3
# FILE: tools/secret_scan.py
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set

# ---- repo root helper ----
def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


REPO_ROOT = _find_repo_root(Path.cwd())

# ---- heuristics / patterns ----
MAX_FILE_BYTES_DEFAULT = 2_000_000  # 2 MB
BINARY_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyd",
    ".db",
    ".sqlite",
    ".duckdb",
    ".parquet",
    ".pkl",
    ".joblib",
    ".bin",
    ".ico",
    ".woff",
    ".woff2",
}

SKIP_DIR_PARTS = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "02_wardrobe_images",
    "03_database",
    "04_user_data",
    "docs/_snapshot",
}

IGNORE_MARKER = "secret-scan:ignore"

# OpenAI keys (broad; catches sk-..., sk-proj-..., etc.)
RE_OPENAI_KEY = re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")
# JWT (common)
RE_JWT = re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")
# Private key blocks
RE_PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
# AWS access key id (common)
RE_AWS_AKIA = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# “Key assignment” heuristic: VAR=VALUE where VALUE is long enough
RE_ASSIGN = re.compile(
    r"""(?ix)
    \b([A-Z0-9_]{3,60})\b
    \s*[:=]\s*
    (["']?)([^"'\r\n]+)\2
    """
)

SENSITIVE_NAME_TOKENS = (
    "API_KEY",
    "OPENAI_API_KEY",
    "WARDROBE_API_KEY",
    "TOKEN",
    "ACCESS_TOKEN",
    "REFRESH_TOKEN",
    "AUTHORIZATION",
    "SECRET",
    "PASSWORD",
    "PRIVATE_KEY",
)

PLACEHOLDER_VALUES = {
    "",
    "null",
    "none",
    "changeme",
    "change_me",
    "replace_me",
    "your_key_here",
    "redacted",
    "***redacted***",
    "***REDACTED***",
    "xxxxx",
    "xxx",
    "test",
    "testkey",
    "dummy",
    "dummykey",
}


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    snippet: str


def _is_probably_binary(data: bytes) -> bool:
    return b"\x00" in data


def _should_skip_path(p: Path) -> bool:
    parts = {x.lower() for x in p.parts}
    for s in SKIP_DIR_PARTS:
        if s.lower() in parts:
            return True
    if p.suffix.lower() in BINARY_EXTS:
        return True
    return False


def scan_text(text: str, rel_path: str) -> List[Finding]:
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if IGNORE_MARKER in line:
            continue

        if RE_PRIVATE_KEY.search(line):
            findings.append(Finding(rel_path, i, "private_key_block", line.strip()[:200]))
            continue
        if RE_OPENAI_KEY.search(line):
            findings.append(Finding(rel_path, i, "openai_key", line.strip()[:200]))
            continue
        if RE_JWT.search(line):
            findings.append(Finding(rel_path, i, "jwt_token", line.strip()[:200]))
            continue
        if RE_AWS_AKIA.search(line):
            findings.append(Finding(rel_path, i, "aws_access_key_id", line.strip()[:200]))
            continue

        m = RE_ASSIGN.search(line)
        if m:
            name = m.group(1)
            val = (m.group(3) or "").strip()
            name_up = name.upper()

            if any(tok in name_up for tok in SENSITIVE_NAME_TOKENS):
                val_low = val.lower()
                if val_low in PLACEHOLDER_VALUES:
                    continue
                if len(val) < 20:
                    continue
                if RE_OPENAI_KEY.search(val) or RE_JWT.search(val) or val.startswith("Bearer "):
                    findings.append(Finding(rel_path, i, "sensitive_assignment", line.strip()[:200]))
                    continue
                findings.append(Finding(rel_path, i, "sensitive_assignment", f"{name}=<redacted>"))

    return findings


def _display_path(path: Path, repo_root: Path) -> str:
    """
    If path is inside repo_root => show relative.
    Else => show absolute. (Important for tests using tmp_path)
    """
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except Exception:
        return str(path.resolve())


def scan_file(path: Path, repo_root: Path, max_bytes: int) -> List[Finding]:
    if _should_skip_path(path):
        return []

    rel = _display_path(path, repo_root)

    try:
        st = path.stat()
        if st.st_size > max_bytes:
            return [Finding(rel, 1, "file_too_large_skipped", f"size={st.st_size}")]
    except Exception:
        pass

    try:
        data = path.read_bytes()
    except Exception as e:
        return [Finding(rel, 1, "read_error", str(e))]

    if _is_probably_binary(data):
        return []

    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        text = data.decode(errors="replace")

    return scan_text(text, rel)


def scan_paths(paths: Sequence[Path], repo_root: Path, max_bytes: int) -> List[Finding]:
    all_findings: List[Finding] = []
    for p in paths:
        if not p.exists() or not p.is_file():
            continue
        all_findings.extend(scan_file(p, repo_root, max_bytes))
    return all_findings


def _git_list_files(mode: str, repo_root: Path) -> List[Path]:
    if mode == "staged":
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"]
    elif mode == "tracked":
        cmd = ["git", "ls-files"]
    else:
        raise ValueError(mode)

    r = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git command failed")

    files = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        files.append((repo_root / line).resolve())
    return files


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Secret scanner (staged or tracked).")
    ap.add_argument("--mode", choices=["staged", "tracked", "paths"], default="staged")
    ap.add_argument("--max-bytes", type=int, default=MAX_FILE_BYTES_DEFAULT)
    ap.add_argument("--paths", nargs="*", default=[], help="Used when --mode paths")
    ap.add_argument("--repo-root", type=str, default=str(REPO_ROOT))
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()

    try:
        if args.mode == "paths":
            paths = [Path(p).resolve() for p in args.paths]
        else:
            paths = _git_list_files(args.mode, repo_root)

        findings = scan_paths(paths, repo_root, args.max_bytes)
        bad = [f for f in findings if f.kind not in {"file_too_large_skipped", "read_error"}]

        if not bad:
            return 0

        print("❌ Secret scan FAILED. Findings:")
        for f in bad[:200]:
            print(f" - {f.path}:{f.line} [{f.kind}] {f.snippet}")
        if len(bad) > 200:
            print(f" ... and {len(bad) - 200} more")
        print()
        print(f"Tip: add '{IGNORE_MARKER}' to a line to suppress a known-safe match.")
        return 2

    except Exception as e:
        print(f"secret_scan error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
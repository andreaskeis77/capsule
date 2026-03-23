#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence


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

# Concrete secret-like patterns.
RE_OPENAI_KEY = re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")
RE_JWT = re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
RE_AWS_AKIA = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# Key assignment heuristic: intentionally conservative.
# Only uppercase/env-style names are treated as potentially sensitive assignments.
RE_ASSIGN = re.compile(
    r"""
    \b([A-Z][A-Z0-9_]{2,60})\b
    \s*[:=]\s*
    (["']?)([^"'\r\n]+)\2
    """,
    flags=re.IGNORECASE | re.VERBOSE,
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
    "xxxxx",
    "xxx",
    "test",
    "testkey",
    "dummy",
    "dummykey",
}

SAFE_ASSIGNMENT_PREFIXES = (
    "x_",
    "request_",
    "response_",
    "normalized_",
)

SAFE_ASSIGNMENT_NAMES = {
    "token",
    "tokens",
    "normalized_token",
    "request_token",
    "csrf_token",
}

SAFE_CALL_SNIPPETS = (
    "Header(",
    "Query(",
    "Path(",
    "Cookie(",
    "Body(",
    ".set(",
    "_tokenize(",
    ".strip(",
    ".lower(",
)


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    snippet: str


def _is_probably_binary(data: bytes) -> bool:
    return b"\x00" in data


def _should_skip_path(p: Path) -> bool:
    parts_lower = {part.lower() for part in p.parts}
    for s in SKIP_DIR_PARTS:
        if s.lower() in parts_lower:
            return True
    return p.suffix.lower() in BINARY_EXTS


def _looks_like_sensitive_assignment(name: str, val: str, line: str) -> bool:
    name_low = name.lower()
    name_up = name.upper()
    val_low = val.strip().lower()

    if name_low in SAFE_ASSIGNMENT_NAMES:
        return False
    if any(name_low.startswith(prefix) for prefix in SAFE_ASSIGNMENT_PREFIXES):
        return False
    if any(snippet in line for snippet in SAFE_CALL_SNIPPETS):
        return False
    if not any(tok in name_up for tok in SENSITIVE_NAME_TOKENS):
        return False
    if val_low in PLACEHOLDER_VALUES:
        return False
    if len(val.strip()) < 20:
        return False
    return True


def scan_text(text: str, rel_path: str = "") -> List[Finding]:
    findings: List[Finding] = []
    for i, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
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
        if not m:
            continue

        name = m.group(1)
        val = (m.group(3) or "").strip()
        if not _looks_like_sensitive_assignment(name, val, line):
            continue

        if RE_OPENAI_KEY.search(val) or RE_JWT.search(val) or val.startswith("Bearer "):
            findings.append(Finding(rel_path, i, "sensitive_assignment", line.strip()[:200]))
            continue

        findings.append(Finding(rel_path, i, "sensitive_assignment", f"{name}="))
    return findings


def _display_path(path: Path, repo_root: Path) -> str:
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

    files: List[Path] = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if line:
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

        print("Secret scan FAILED. Findings:")
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

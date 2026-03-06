
#!/usr/bin/env python3
"""
repo_metrics_bold.py

Comprehensive repository metrics analyzer for software-engineering oriented repos.

v3 / phase-0 goals:
- default to measuring the *Git repository* rather than the whole workspace
- support explicit scan modes (tracked / git-visible / filesystem)
- handle UTF-8 BOM cleanly for Python parsing
- separate repository scopes (tracked, core, production, docs, workspace-noise)
- reduce false risk / hotspot inflation from logs, assets and staging trees
- detect exact duplicate / mirrored text files
- emit quality gates and richer JSON / CSV / Markdown outputs
- emit phase-0 hygiene findings and cleanup candidates
- keep canonical filenames stable so the script can be overwritten in place

Baseline operation has no third-party dependency.
Optional extras if installed: radon, pytest-cov.
"""
from __future__ import annotations

import argparse
import ast
import csv
import fnmatch
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


# -----------------------------
# Configuration
# -----------------------------
DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".idea",
    ".vscode",
    ".coverage",
    "htmlcov",
    ".DS_Store",
}

DEFAULT_EXCLUDE_GLOBS = {
    "docs/_metrics/**",
    "**/.ipynb_checkpoints/**",
}

TEXT_EXTENSIONS = {
    ".py", ".pyi", ".pyw",
    ".js", ".jsx", ".ts", ".tsx",
    ".html", ".htm", ".css", ".scss", ".less",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env",
    ".md", ".rst", ".txt", ".csv", ".tsv", ".sql", ".log",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
    ".xml", ".svg", ".jinja", ".j2",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}
TEMPLATE_EXTENSIONS = {".html", ".htm", ".jinja", ".j2"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}
DATA_EXTENSIONS = {".csv", ".tsv", ".sqlite", ".db", ".parquet"}
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf"}
LOG_EXTENSIONS = {".log"}
TEST_FILE_PATTERNS = ["test_*.py", "*_test.py"]

COMMENT_SYNTAX = {
    ".py": ("#", None, None),
    ".pyi": ("#", None, None),
    ".js": ("//", "/*", "*/"),
    ".jsx": ("//", "/*", "*/"),
    ".ts": ("//", "/*", "*/"),
    ".tsx": ("//", "/*", "*/"),
    ".css": (None, "/*", "*/"),
    ".scss": (None, "/*", "*/"),
    ".less": (None, "/*", "*/"),
    ".java": ("//", "/*", "*/"),
    ".go": ("//", "/*", "*/"),
    ".rs": ("//", "/*", "*/"),
    ".php": ("//", "/*", "*/"),
    ".sql": ("--", "/*", "*/"),
    ".sh": ("#", None, None),
    ".bash": ("#", None, None),
    ".zsh": ("#", None, None),
    ".ps1": ("#", "<#", "#>"),
    ".bat": ("REM", None, None),
    ".cmd": ("REM", None, None),
    ".html": (None, "<!--", "-->"),
    ".htm": (None, "<!--", "-->"),
    ".xml": (None, "<!--", "-->"),
    ".svg": (None, "<!--", "-->"),
    ".log": (None, None, None),
}

LANGUAGE_BY_EXTENSION = {
    ".py": "Python", ".pyi": "Python", ".pyw": "Python",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "CSS", ".less": "CSS",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".ini": "INI", ".cfg": "Config", ".env": "Config",
    ".md": "Markdown", ".rst": "reStructuredText", ".txt": "Text",
    ".csv": "CSV", ".tsv": "TSV", ".sql": "SQL",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".ps1": "PowerShell", ".bat": "Batch", ".cmd": "Batch",
    ".xml": "XML", ".svg": "SVG", ".log": "LOG",
}

ENGINEERING_ROLES = {"application", "tooling", "template", "test", "config"}
PRODUCTION_ROLES = {"application", "tooling", "template", "config"}
NON_ENGINEERING_ROLES = {"documentation", "asset", "data", "log", "other"}

ROLE_RISK_WEIGHT = {
    "application": 1.00,
    "tooling": 0.90,
    "template": 0.75,
    "test": 0.60,
    "config": 0.35,
    "documentation": 0.10,
    "asset": 0.00,
    "data": 0.00,
    "log": 0.00,
    "other": 0.20,
}

BACKUP_FILE_GLOBS = {"*.bak", "*.tmp", "*.orig", "*.rej", "*~"}
GENERATED_DATA_HINTS = ("export", "snapshot", "dump", "handoff", "report")
STAGING_DIR_HINTS = {"_release_staging", "_snapshot"}
POLICY_DIRTY_EXPORT_NAMES = {"wardrobe_export.json"}
PHASE0_HIGH_VALUE_DIRS = {"src", "templates", "ontology", "tests", "tools", "docs"}


# -----------------------------
# Utilities
# -----------------------------
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    values = sorted(values)
    idx = (len(values) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[lo]
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac


def clamp(v: float, low: float, high: float) -> float:
    return max(low, min(high, v))


def read_text_normalized(path: Path) -> str:
    # utf-8-sig strips BOM cleanly and fixes the FEFF parse issue seen in v1.
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()


def sha1_bytes(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def markdown_escape(value: Any) -> str:
    return str(value).replace("|", r"\|")


# -----------------------------
# Data classes
# -----------------------------
@dataclass
class LineMetrics:
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    doc_lines: int = 0


@dataclass
class CoverageMetrics:
    statements: int = 0
    missing: int = 0
    excluded: int = 0
    branches: int = 0
    partial_branches: int = 0
    covered_branches: int = 0
    percent_covered: float = 0.0


@dataclass
class GitMetrics:
    tracked: bool = False
    visible_to_git: bool = False
    commit_count: int = 0
    additions: int = 0
    deletions: int = 0
    churn: int = 0
    authors: list[str] = field(default_factory=list)
    last_commit_ts: int | None = None
    last_commit_iso: str | None = None


@dataclass
class PythonFunctionMetric:
    file: str
    qualified_name: str
    kind: str
    lineno: int
    end_lineno: int
    length: int
    cyclomatic_complexity: int
    max_nesting: int
    arg_count: int
    has_docstring: bool


@dataclass
class PythonFileMetrics:
    syntax_error: str | None = None
    module_name: str | None = None
    class_count: int = 0
    function_count: int = 0
    method_count: int = 0
    test_function_count: int = 0
    module_docstring: bool = False
    docstring_lines: int = 0
    import_count: int = 0
    internal_import_count: int = 0
    external_import_count: int = 0
    imported_internal_modules: list[str] = field(default_factory=list)
    imported_external_modules: list[str] = field(default_factory=list)
    average_function_length: float = 0.0
    max_function_length: int = 0
    average_function_cc: float = 0.0
    max_function_cc: int = 0
    average_max_nesting: float = 0.0
    max_nesting: int = 0
    approx_cyclomatic_complexity: int = 0
    approx_halstead_volume: float = 0.0
    approx_halstead_difficulty: float = 0.0
    approx_halstead_effort: float = 0.0
    approx_maintainability_index: float = 0.0
    radon_mi: float | None = None
    radon_cc_average: float | None = None
    radon_cc_max: float | None = None
    radon_available: bool = False


@dataclass
class FileRecord:
    path: str
    name: str
    extension: str
    language: str
    role: str
    top_level_dir: str
    size_bytes: int
    is_binary: bool
    is_text: bool
    lines: LineMetrics
    git: GitMetrics
    coverage: CoverageMetrics
    python: PythonFileMetrics | None = None
    content_sha1: str | None = None
    risk_score: float = 0.0
    hotspot_score: float = 0.0
    notes: list[str] = field(default_factory=list)


# -----------------------------
# Subprocess helpers
# -----------------------------
def run(cmd: list[str], cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
        encoding="utf-8",
        errors="replace",
    )


# -----------------------------
# File and path helpers
# -----------------------------
def git_available(repo_root: Path) -> bool:
    return shutil.which("git") is not None and (repo_root / ".git").exists()


def git_head_info(repo_root: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "available": False,
        "branch": None,
        "head_sha": None,
        "commit_count": 0,
        "tracked_files": 0,
        "git_visible_files": 0,
        "dirty": None,
    }
    if not git_available(repo_root):
        return info
    info["available"] = True

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if branch.returncode == 0:
        info["branch"] = branch.stdout.strip()

    sha = run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if sha.returncode == 0:
        info["head_sha"] = sha.stdout.strip()

    count = run(["git", "rev-list", "--count", "HEAD"], cwd=repo_root)
    if count.returncode == 0:
        try:
            info["commit_count"] = int(count.stdout.strip())
        except ValueError:
            pass

    tracked = git_tracked_set(repo_root)
    info["tracked_files"] = len(tracked)
    info["git_visible_files"] = len(git_visible_set(repo_root))

    dirty = run(["git", "status", "--porcelain"], cwd=repo_root)
    if dirty.returncode == 0:
        info["dirty"] = bool(dirty.stdout.strip())

    return info


def git_tracked_set(repo_root: Path) -> set[str]:
    if not git_available(repo_root):
        return set()
    proc = run(["git", "ls-files", "-z"], cwd=repo_root)
    if proc.returncode != 0:
        return set()
    return {x.replace("\\", "/") for x in proc.stdout.split("\x00") if x}


def git_visible_set(repo_root: Path) -> set[str]:
    if not git_available(repo_root):
        return set()
    proc = run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=repo_root)
    if proc.returncode != 0:
        return set()
    return {x.replace("\\", "/") for x in proc.stdout.split("\x00") if x}


def collect_git_file_metrics(repo_root: Path) -> dict[str, GitMetrics]:
    metrics: dict[str, GitMetrics] = {}
    tracked = git_tracked_set(repo_root)
    visible = git_visible_set(repo_root)
    for path in visible:
        metrics[path] = GitMetrics(tracked=path in tracked, visible_to_git=True)
    if not git_available(repo_root):
        return metrics

    proc = run(["git", "log", "--numstat", "--format=commit%x09%H%x09%ct%x09%an"], cwd=repo_root)
    if proc.returncode != 0:
        return metrics

    current_author = None
    current_ts: int | None = None
    for raw in proc.stdout.splitlines():
        if raw.startswith("commit\t"):
            _, _sha, ts, author = raw.split("\t", 3)
            current_author = author
            try:
                current_ts = int(ts)
            except ValueError:
                current_ts = None
            continue
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) != 3:
            continue
        add_s, del_s, file_s = parts
        file_s = file_s.replace("\\", "/")
        entry = metrics.setdefault(file_s, GitMetrics(tracked=file_s in tracked, visible_to_git=file_s in visible))
        entry.commit_count += 1
        if add_s.isdigit():
            entry.additions += int(add_s)
        if del_s.isdigit():
            entry.deletions += int(del_s)
        entry.churn = entry.additions + entry.deletions
        if current_author and current_author not in entry.authors:
            entry.authors.append(current_author)
        if current_ts is not None and (entry.last_commit_ts is None or current_ts > entry.last_commit_ts):
            entry.last_commit_ts = current_ts
            entry.last_commit_iso = datetime.fromtimestamp(current_ts, tz=timezone.utc).replace(microsecond=0).isoformat()

    return metrics


def should_exclude_rel(rel: Path, exclude_names: set[str], exclude_globs: set[str]) -> bool:
    parts = set(rel.parts)
    if any(part in exclude_names for part in parts):
        return True
    posix = rel.as_posix()
    return any(fnmatch.fnmatch(posix, pat) for pat in exclude_globs)


def is_probably_binary(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            chunk = fh.read(8192)
    except OSError:
        return True
    if b"\x00" in chunk:
        return True
    if not chunk:
        return False
    text_chars = bytes(range(32, 127)) + b"\n\r\t\b\f"
    nontext = sum(byte not in text_chars for byte in chunk)
    return (nontext / len(chunk)) > 0.30


def infer_role(rel_path: Path) -> str:
    ext = rel_path.suffix.lower()
    parts = {p.lower() for p in rel_path.parts}
    name = rel_path.name.lower()
    posix_path = rel_path.as_posix().lower()

    if ext in LOG_EXTENSIONS or "logs" in parts:
        return "log"
    if "tests" in parts or any(fnmatch.fnmatch(name, pat) for pat in TEST_FILE_PATTERNS):
        return "test"
    if "docs" in parts or ext in DOC_EXTENSIONS:
        return "documentation"
    if "templates" in parts or ext in TEMPLATE_EXTENSIONS:
        return "template"
    if ext in DATA_EXTENSIONS or "data" in parts:
        return "data"
    if ext == ".json" and any(hint in name for hint in GENERATED_DATA_HINTS):
        return "data"
    if ext in CONFIG_EXTENSIONS or name in {"requirements.txt", "pytest.ini", ".gitignore", ".coveragerc", "pyproject.toml"}:
        return "config"
    if ext in ASSET_EXTENSIONS:
        return "asset"
    if posix_path.startswith("tools/"):
        return "tooling"
    if posix_path.startswith("src/"):
        return "application"
    return "other"


def is_backup_like(rel_path: Path) -> bool:
    name = rel_path.name.lower()
    return any(fnmatch.fnmatch(name, pat) for pat in BACKUP_FILE_GLOBS)


def is_staging_like(rel_path: Path) -> bool:
    return any(part.lower() in STAGING_DIR_HINTS for part in rel_path.parts)


def is_generated_data_like(rel_path: Path, role: str) -> bool:
    name = rel_path.name.lower()
    posix = rel_path.as_posix().lower()
    if name in POLICY_DIRTY_EXPORT_NAMES:
        return True
    if role == "data" and any(hint in name for hint in GENERATED_DATA_HINTS):
        return True
    if any(hint in posix for hint in ("/exports/", "/snapshots/", "/handoff/", "/dumps/")):
        return True
    return False


def infer_language(path: Path) -> str:
    ext = path.suffix.lower()
    return LANGUAGE_BY_EXTENSION.get(ext, ext[1:].upper() if ext else "No Extension")


def top_level_dir(rel_path: Path) -> str:
    return rel_path.parts[0] if len(rel_path.parts) > 1 else "."


def module_name_from_path(rel_path: Path) -> str | None:
    if rel_path.suffix != ".py":
        return None
    parts = list(rel_path.with_suffix("").parts)
    if not parts:
        return None
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


# -----------------------------
# Scan path collection
# -----------------------------
def collect_scan_rel_paths(repo_root: Path, args: argparse.Namespace) -> list[Path]:
    mode = args.scan_mode
    if mode == "auto":
        mode = "tracked" if git_available(repo_root) else "filesystem"

    rels: list[Path] = []
    if mode == "tracked":
        for rel in sorted(git_tracked_set(repo_root)):
            rel_path = Path(rel)
            if not should_exclude_rel(rel_path, args.excludes, args.exclude_globs):
                full = repo_root / rel_path
                if full.exists() and full.is_file():
                    rels.append(rel_path)
        return rels

    if mode == "git-visible":
        for rel in sorted(git_visible_set(repo_root)):
            rel_path = Path(rel)
            if not should_exclude_rel(rel_path, args.excludes, args.exclude_globs):
                full = repo_root / rel_path
                if full.exists() and full.is_file():
                    rels.append(rel_path)
        return rels

    # filesystem
    for path in repo_root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(repo_root)
        if should_exclude_rel(rel, args.excludes, args.exclude_globs):
            continue
        rels.append(rel)
    rels.sort(key=lambda p: p.as_posix())
    return rels


# -----------------------------
# Line counting
# -----------------------------
def count_lines_from_text(content: str, role: str, ext: str) -> LineMetrics:
    line_comment, block_start, block_end = COMMENT_SYNTAX.get(ext, (None, None, None))
    metrics = LineMetrics()
    in_block = False
    lines = content.splitlines()

    if role == "documentation":
        metrics.total_lines = len(lines)
        for raw in lines:
            line = raw.strip()
            if not line:
                metrics.blank_lines += 1
            else:
                metrics.doc_lines += 1
        return metrics

    for raw in lines:
        metrics.total_lines += 1
        stripped = raw.strip()
        if not stripped:
            metrics.blank_lines += 1
            continue

        if in_block:
            metrics.comment_lines += 1
            if block_end and block_end in stripped:
                in_block = False
            continue

        if block_start and block_end and stripped.startswith(block_start):
            metrics.comment_lines += 1
            if block_end not in stripped[len(block_start):]:
                in_block = True
            continue

        if line_comment:
            if stripped.startswith(line_comment):
                metrics.comment_lines += 1
                continue

        metrics.code_lines += 1

    return metrics


# -----------------------------
# Python AST metrics
# -----------------------------
OPERAND_NODES = (ast.Name, ast.Attribute, ast.Constant)


class HalsteadVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.operators: list[str] = []
        self.operands: list[str] = []

    def generic_visit(self, node: ast.AST) -> None:
        node_name = type(node).__name__
        if isinstance(node, (ast.BinOp, ast.BoolOp, ast.UnaryOp, ast.Compare, ast.If, ast.For, ast.AsyncFor,
                             ast.While, ast.With, ast.AsyncWith, ast.Try, ast.Call, ast.Return,
                             ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Assert, ast.Raise,
                             ast.Lambda, ast.IfExp, ast.DictComp, ast.ListComp, ast.SetComp,
                             ast.GeneratorExp, ast.Match)):
            self.operators.append(node_name)
        elif isinstance(node, OPERAND_NODES):
            if isinstance(node, ast.Name):
                self.operands.append(node.id)
            elif isinstance(node, ast.Attribute):
                self.operands.append(node.attr)
            elif isinstance(node, ast.Constant):
                self.operands.append(repr(node.value))
        super().generic_visit(node)


def compute_halstead_from_tree(tree: ast.AST) -> tuple[float, float, float]:
    v = HalsteadVisitor()
    v.visit(tree)
    n1 = len(set(v.operators))
    n2 = len(set(v.operands))
    N1 = len(v.operators)
    N2 = len(v.operands)
    vocabulary = n1 + n2
    length = N1 + N2
    volume = length * math.log2(vocabulary) if vocabulary > 1 and length > 0 else 0.0
    difficulty = ((n1 / 2) * (N2 / n2)) if n2 else 0.0
    effort = difficulty * volume
    return volume, difficulty, effort


def maintainability_index(volume: float, cc: float, sloc: int) -> float:
    sloc = max(sloc, 1)
    volume = max(volume, 1.0)
    mi = (171 - 5.2 * math.log(volume) - 0.23 * cc - 16.2 * math.log(sloc)) * 100 / 171
    return clamp(mi, 0.0, 100.0)


class ComplexityCounter(ast.NodeVisitor):
    def __init__(self) -> None:
        self.cc = 1
        self.max_depth = 0
        self.current_depth = 0

    def bump(self, amount: int = 1) -> None:
        self.cc += amount

    def descend(self) -> None:
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

    def ascend(self) -> None:
        self.current_depth = max(0, self.current_depth - 1)

    def visit_If(self, node: ast.If) -> None:
        self.bump(1)
        self.descend()
        self.generic_visit(node)
        self.ascend()

    def visit_For(self, node: ast.For) -> None:
        self.bump(1)
        self.descend()
        self.generic_visit(node)
        self.ascend()

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.bump(1)
        self.descend()
        self.generic_visit(node)
        self.ascend()

    def visit_While(self, node: ast.While) -> None:
        self.bump(1)
        self.descend()
        self.generic_visit(node)
        self.ascend()

    def visit_Try(self, node: ast.Try) -> None:
        self.bump(max(1, len(node.handlers)))
        self.descend()
        self.generic_visit(node)
        self.ascend()

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.bump(max(0, len(node.values) - 1))
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.bump(1)
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.bump(1)
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.bump(1)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self.bump(max(1, len(node.cases)))
        self.descend()
        self.generic_visit(node)
        self.ascend()


class FunctionCollector(ast.NodeVisitor):
    def __init__(self, rel_path: Path) -> None:
        self.rel_path = rel_path
        self.functions: list[PythonFunctionMetric] = []
        self.class_stack: list[str] = []

    def _record(self, node: ast.AST, name: str, kind: str) -> None:
        cc_counter = ComplexityCounter()
        cc_counter.visit(node)
        lineno = getattr(node, "lineno", 1)
        end_lineno = getattr(node, "end_lineno", lineno)
        args = getattr(node, "args", None)
        arg_count = 0
        if args is not None:
            arg_count = len(getattr(args, "posonlyargs", [])) + len(args.args) + len(args.kwonlyargs)
            if args.vararg:
                arg_count += 1
            if args.kwarg:
                arg_count += 1
        has_docstring = ast.get_docstring(node) is not None
        qn = ".".join([*self.class_stack, name]) if self.class_stack else name
        self.functions.append(
            PythonFunctionMetric(
                file=self.rel_path.as_posix(),
                qualified_name=qn,
                kind=kind,
                lineno=lineno,
                end_lineno=end_lineno,
                length=max(1, end_lineno - lineno + 1),
                cyclomatic_complexity=cc_counter.cc,
                max_nesting=cc_counter.max_depth,
                arg_count=arg_count,
                has_docstring=has_docstring,
            )
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = "method" if self.class_stack else "function"
        self._record(node, node.name, kind)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        kind = "method" if self.class_stack else "function"
        self._record(node, node.name, kind)
        self.generic_visit(node)


def import_targets(tree: ast.AST) -> list[str]:
    targets: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = "." * node.level + module
            targets.append(module)
    return targets


def resolve_internal_imports(module_name: str | None, imports: list[str], module_index: set[str]) -> tuple[list[str], list[str]]:
    internal: set[str] = set()
    external: set[str] = set()

    for imp in imports:
        normalized = imp
        if imp.startswith("."):
            if not module_name:
                external.add(imp)
                continue
            level = len(imp) - len(imp.lstrip("."))
            suffix = imp.lstrip(".")
            module_parts = module_name.split(".")[:-1]
            if level > len(module_parts):
                normalized = suffix
            else:
                base = module_parts[: len(module_parts) - level + 1]
                normalized = ".".join(base + ([suffix] if suffix else []))

        matched_internal = None
        if normalized in module_index:
            matched_internal = normalized
        else:
            prefixes = normalized.split(".")
            for i in range(len(prefixes), 0, -1):
                candidate = ".".join(prefixes[:i])
                if candidate in module_index:
                    matched_internal = candidate
                    break
        if matched_internal:
            internal.add(matched_internal)
        else:
            external.add(normalized)

    return sorted(internal), sorted(external)


def compute_docstring_lines(tree: ast.AST) -> int:
    lines = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            exprs = getattr(node, "body", [])
            if exprs and isinstance(exprs[0], ast.Expr):
                value = exprs[0].value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    start = getattr(exprs[0], "lineno", 0)
                    end = getattr(exprs[0], "end_lineno", start)
                    lines += max(1, end - start + 1)
    return lines


def compute_python_metrics(path: Path, rel_path: Path, code_lines: int, module_index: set[str], use_radon: bool) -> tuple[PythonFileMetrics, list[PythonFunctionMetric]]:
    module_name = module_name_from_path(rel_path)
    try:
        source = read_text_normalized(path)
    except OSError as exc:
        return PythonFileMetrics(syntax_error=str(exc), module_name=module_name), []

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return PythonFileMetrics(syntax_error=str(exc), module_name=module_name), []

    collector = FunctionCollector(rel_path)
    collector.visit(tree)
    funcs = collector.functions

    imports = import_targets(tree)
    internal_imports, external_imports = resolve_internal_imports(module_name, imports, module_index)
    volume, difficulty, effort = compute_halstead_from_tree(tree)

    approx_cc = sum(f.cyclomatic_complexity for f in funcs) or 1
    avg_len = statistics.mean(f.length for f in funcs) if funcs else 0.0
    max_len = max((f.length for f in funcs), default=0)
    avg_cc = statistics.mean(f.cyclomatic_complexity for f in funcs) if funcs else 0.0
    max_cc = max((f.cyclomatic_complexity for f in funcs), default=0)
    avg_nesting = statistics.mean(f.max_nesting for f in funcs) if funcs else 0.0
    max_nesting = max((f.max_nesting for f in funcs), default=0)

    pfm = PythonFileMetrics(
        module_name=module_name,
        class_count=sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree)),
        function_count=sum(1 for f in funcs if f.kind == "function"),
        method_count=sum(1 for f in funcs if f.kind == "method"),
        test_function_count=sum(1 for f in funcs if rel_path.name.startswith("test_") or f.qualified_name.split(".")[-1].startswith("test_")),
        module_docstring=ast.get_docstring(tree) is not None,
        docstring_lines=compute_docstring_lines(tree),
        import_count=len(imports),
        internal_import_count=len(internal_imports),
        external_import_count=len(external_imports),
        imported_internal_modules=internal_imports,
        imported_external_modules=external_imports,
        average_function_length=round(avg_len, 2),
        max_function_length=max_len,
        average_function_cc=round(avg_cc, 2),
        max_function_cc=max_cc,
        average_max_nesting=round(avg_nesting, 2),
        max_nesting=max_nesting,
        approx_cyclomatic_complexity=approx_cc,
        approx_halstead_volume=round(volume, 2),
        approx_halstead_difficulty=round(difficulty, 2),
        approx_halstead_effort=round(effort, 2),
        approx_maintainability_index=round(maintainability_index(volume, approx_cc, code_lines), 2),
    )

    if use_radon:
        try:
            from radon.complexity import cc_visit
            from radon.metrics import h_visit, mi_visit

            pfm.radon_available = True
            blocks = cc_visit(source)
            if blocks:
                cc_values = [b.complexity for b in blocks]
                pfm.radon_cc_average = round(statistics.mean(cc_values), 2)
                pfm.radon_cc_max = max(cc_values)
            mi = mi_visit(source, multi=True)
            pfm.radon_mi = round(float(mi), 2)
            _ = h_visit(source)
        except Exception:
            pass

    return pfm, funcs


# -----------------------------
# Coverage ingestion / execution
# -----------------------------
def parse_coverage_json(path: Path) -> tuple[dict[str, CoverageMetrics], dict[str, Any]]:
    per_file: dict[str, CoverageMetrics] = {}
    summary: dict[str, Any] = {"available": False}
    if not path.exists():
        return per_file, summary
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return per_file, summary

    summary = data.get("totals", {}) | {"available": True}
    files = data.get("files", {})
    for file_path, item in files.items():
        s = item.get("summary", {})
        norm = file_path.replace("\\", "/")
        cm = CoverageMetrics(
            statements=s.get("num_statements", 0),
            missing=s.get("missing_lines", 0),
            excluded=s.get("excluded_lines", 0),
            branches=s.get("num_branches", 0),
            partial_branches=s.get("num_partial_branches", 0),
            covered_branches=s.get("covered_branches", 0),
            percent_covered=float(s.get("percent_covered", 0.0) or 0.0),
        )
        per_file[norm] = cm
    return per_file, summary


def maybe_run_pytest_coverage(repo_root: Path, args: argparse.Namespace, out_dir: Path) -> Path | None:
    if not args.run_tests:
        return None
    pytest_cmd = [sys.executable, "-m", "pytest", "-q"]
    if args.pytest_target:
        pytest_cmd.append(args.pytest_target)
    if args.coverage_target:
        pytest_cmd.extend([
            f"--cov={args.coverage_target}",
            "--cov-branch",
            f"--cov-report=json:{(out_dir / 'coverage.json').as_posix()}",
            "--cov-report=term",
        ])
    if args.cov_context_tests:
        pytest_cmd.append("--cov-context=test")
    if args.pytest_extra:
        pytest_cmd.extend(args.pytest_extra)

    proc = run(pytest_cmd, cwd=repo_root)
    (out_dir / "pytest_coverage.stdout.log").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "pytest_coverage.stderr.log").write_text(proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        return None
    cov = out_dir / "coverage.json"
    return cov if cov.exists() else None


# -----------------------------
# Aggregation and scoring
# -----------------------------
def aggregate_lines(records: list[FileRecord]) -> dict[str, int]:
    totals = LineMetrics()
    for r in records:
        totals.total_lines += r.lines.total_lines
        totals.code_lines += r.lines.code_lines
        totals.comment_lines += r.lines.comment_lines
        totals.blank_lines += r.lines.blank_lines
        totals.doc_lines += r.lines.doc_lines
    return asdict(totals)


def summarize_by(records: list[FileRecord], key_fn) -> list[dict[str, Any]]:
    groups: dict[str, list[FileRecord]] = defaultdict(list)
    for r in records:
        groups[key_fn(r)].append(r)

    rows: list[dict[str, Any]] = []
    for key, items in groups.items():
        line_totals = aggregate_lines(items)
        rows.append({
            "key": key,
            "file_count": len(items),
            "size_bytes": sum(i.size_bytes for i in items),
            "code_lines": line_totals["code_lines"],
            "comment_lines": line_totals["comment_lines"],
            "blank_lines": line_totals["blank_lines"],
            "doc_lines": line_totals["doc_lines"],
            "total_lines": line_totals["total_lines"],
            "avg_risk_score": round(statistics.mean(i.risk_score for i in items), 2) if items else 0.0,
            "avg_hotspot_score": round(statistics.mean(i.hotspot_score for i in items), 2) if items else 0.0,
            "total_churn": sum(i.git.churn for i in items),
            "tracked_files": sum(1 for i in items if i.git.tracked),
            "binary_files": sum(1 for i in items if i.is_binary),
        })
    rows.sort(key=lambda x: (-x["code_lines"], x["key"]))
    return rows


def classify_size_bucket(code_lines: int) -> str:
    if code_lines >= 1000:
        return "XL (1000+)"
    if code_lines >= 500:
        return "L (500-999)"
    if code_lines >= 200:
        return "M (200-499)"
    if code_lines >= 50:
        return "S (50-199)"
    return "XS (<50)"


def risk_label(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def compute_scores(records: list[FileRecord], coverage_available: bool) -> None:
    size_values = [r.lines.code_lines for r in records if r.role in ENGINEERING_ROLES and r.lines.code_lines > 0]
    churn_values = [r.git.churn for r in records if r.role in ENGINEERING_ROLES and r.git.churn > 0]
    cc_values: list[float] = []
    mi_values: list[float] = []
    for r in records:
        if r.python and r.role in ENGINEERING_ROLES:
            cc_values.append(float(r.python.radon_cc_average or r.python.average_function_cc or 0))
            mi_values.append(float(r.python.radon_mi or r.python.approx_maintainability_index or 0))

    p95_size = percentile(size_values, 0.95) or 1.0
    p95_churn = percentile(churn_values, 0.95) or 1.0
    p95_cc = percentile(cc_values, 0.95) or 1.0

    for r in records:
        weight = ROLE_RISK_WEIGHT.get(r.role, 0.2)

        size_factor = safe_div(min(r.lines.code_lines, p95_size), p95_size) * 25
        churn_factor = safe_div(min(r.git.churn, p95_churn), p95_churn) * 25

        complexity_value = 0.0
        maintainability_penalty = 0.0
        coverage_penalty = 0.0
        import_penalty = 0.0
        syntax_penalty = 0.0
        ownership_penalty = 0.0

        if r.python:
            complexity_value = float(r.python.radon_cc_average or r.python.average_function_cc or 0)
            mi = float(r.python.radon_mi or r.python.approx_maintainability_index or 0)
            complexity_factor = safe_div(min(complexity_value, p95_cc), p95_cc) * 20
            maintainability_penalty = clamp((60 - mi) / 60, 0, 1) * 20
            import_penalty = clamp(r.python.internal_import_count / 15, 0, 1) * 5
            if r.python.syntax_error:
                syntax_penalty = 12.0
        else:
            complexity_factor = 0.0

        if coverage_available and r.role in PRODUCTION_ROLES:
            if r.coverage.statements > 0:
                coverage_penalty = clamp((85 - r.coverage.percent_covered) / 85, 0, 1) * 8
            else:
                coverage_penalty = 5.0

        if r.role in PRODUCTION_ROLES and r.git.churn >= 100 and len(r.git.authors) <= 1:
            ownership_penalty = 3.0

        raw_risk = size_factor + churn_factor + complexity_factor + maintainability_penalty + coverage_penalty + import_penalty + syntax_penalty + ownership_penalty
        r.risk_score = round(raw_risk * weight, 2)

        hotspot_base = (r.git.churn + 1) * (complexity_value + 1) * math.log2(r.lines.code_lines + 2)
        r.hotspot_score = round(hotspot_base * max(weight, 0.15), 2)

        if r.lines.code_lines >= 500 and r.role in ENGINEERING_ROLES:
            r.notes.append("large-file")
        if r.python and (r.python.radon_mi or r.python.approx_maintainability_index) < 50 and r.role in ENGINEERING_ROLES:
            r.notes.append("low-maintainability")
        if r.python and (r.python.radon_cc_max or r.python.max_function_cc) >= 15 and r.role in ENGINEERING_ROLES:
            r.notes.append("high-complexity-function")
        if coverage_available and r.role in PRODUCTION_ROLES and r.coverage.statements > 0 and r.coverage.percent_covered < 70:
            r.notes.append("low-coverage")
        if coverage_available and r.role in PRODUCTION_ROLES and r.coverage.statements == 0:
            r.notes.append("missing-coverage-data")
        if r.git.churn >= 100 and r.role in ENGINEERING_ROLES:
            r.notes.append("high-churn")
        if r.python and r.python.syntax_error:
            r.notes.append("python-parse-error")
        if r.role == "log":
            r.notes.append("operational-log")
        if r.role == "asset":
            r.notes.append("binary-asset")


# -----------------------------
# Duplicate / shadow detection
# -----------------------------
def detect_exact_duplicates(records: list[FileRecord]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, str], list[FileRecord]] = defaultdict(list)
    for r in records:
        if not r.is_text or not r.content_sha1:
            continue
        groups[(r.size_bytes, r.content_sha1)].append(r)

    rows: list[dict[str, Any]] = []
    for (size, sha1), items in groups.items():
        if len(items) < 2:
            continue
        paths = sorted(i.path for i in items)
        rows.append({
            "duplicate_count": len(items),
            "size_bytes": size,
            "sha1": sha1,
            "paths": " || ".join(paths),
            "tracked_paths": " || ".join(sorted(i.path for i in items if i.git.tracked)),
        })
    rows.sort(key=lambda x: (-x["duplicate_count"], -x["size_bytes"], x["sha1"]))
    return rows


def detect_shadow_duplicates(records: list[FileRecord]) -> list[dict[str, Any]]:
    by_path = {r.path: r for r in records if r.is_text and r.content_sha1}
    paths = sorted(by_path)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for outer in paths:
        for inner in paths:
            if outer == inner:
                continue
            if outer.endswith(inner) and by_path[outer].content_sha1 == by_path[inner].content_sha1:
                key = tuple(sorted((outer, inner)))
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "source_path": inner,
                    "shadow_path": outer,
                    "size_bytes": by_path[inner].size_bytes,
                    "sha1": by_path[inner].content_sha1,
                    "tracked_source": by_path[inner].git.tracked,
                    "tracked_shadow": by_path[outer].git.tracked,
                })
    rows.sort(key=lambda x: (x["source_path"], x["shadow_path"]))
    return rows


# -----------------------------
# Scope summaries and issues
# -----------------------------
def scope_definitions(records: list[FileRecord]) -> dict[str, list[FileRecord]]:
    return {
        "all_scanned": records,
        "tracked_only": [r for r in records if r.git.tracked],
        "git_visible": [r for r in records if r.git.visible_to_git],
        "engineering_core": [r for r in records if r.role in ENGINEERING_ROLES],
        "production_core": [r for r in records if r.role in PRODUCTION_ROLES],
        "tests_only": [r for r in records if r.role == "test"],
        "docs_only": [r for r in records if r.role == "documentation"],
        "workspace_noise": [r for r in records if r.role in {"log", "asset", "data"} or not r.git.tracked],
    }


def build_scope_rows(records: list[FileRecord]) -> list[dict[str, Any]]:
    scopes = scope_definitions(records)
    rows: list[dict[str, Any]] = []
    prod = scopes["production_core"]
    tests = scopes["tests_only"]
    docs = scopes["docs_only"]

    prod_lines = aggregate_lines(prod)
    test_lines = aggregate_lines(tests)
    doc_lines = aggregate_lines(docs)

    for name, items in scopes.items():
        lines = aggregate_lines(items)
        rows.append({
            "scope": name,
            "file_count": len(items),
            "tracked_files": sum(1 for r in items if r.git.tracked),
            "code_lines": lines["code_lines"],
            "doc_lines": lines["doc_lines"],
            "comment_lines": lines["comment_lines"],
            "binary_files": sum(1 for r in items if r.is_binary),
            "total_churn": sum(r.git.churn for r in items),
            "avg_risk_score": round(statistics.mean(r.risk_score for r in items), 2) if items else 0.0,
            "avg_hotspot_score": round(statistics.mean(r.hotspot_score for r in items), 2) if items else 0.0,
        })

    # Attach repo-level ratios to the production row if present.
    for row in rows:
        if row["scope"] == "production_core":
            row["test_to_prod_code_ratio"] = round(safe_div(test_lines["code_lines"], max(prod_lines["code_lines"], 1)), 4)
            row["docs_to_prod_code_ratio"] = round(safe_div(doc_lines["doc_lines"], max(prod_lines["code_lines"], 1)), 4)
            row["comment_density"] = round(safe_div(prod_lines["comment_lines"], max(prod_lines["code_lines"] + prod_lines["comment_lines"], 1)), 4)
    rows.sort(key=lambda x: x["scope"])
    return rows


def collect_policy_findings(records: list[FileRecord], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issue_lookup: dict[tuple[str, str], dict[str, Any]] = {(i.get("path", ""), i.get("kind", "")): i for i in issues}
    findings: list[dict[str, Any]] = []

    for r in sorted(records, key=lambda x: x.path):
        rel = Path(r.path)
        reasons: list[str] = []
        recommendation = "review"
        priority = "medium"

        if r.git.tracked and is_backup_like(rel):
            reasons.append("tracked-backup-file")
            recommendation = "remove-from-repo"
            priority = "high"
        if r.git.tracked and is_staging_like(rel):
            reasons.append("tracked-staging-file")
            recommendation = "remove-from-repo"
            priority = "high"
        if r.git.tracked and is_generated_data_like(rel, r.role):
            reasons.append("tracked-generated-data")
            recommendation = "move-or-ignore"
            priority = "high"
        if r.role in PRODUCTION_ROLES and r.git.churn >= 250:
            reasons.append("high-churn")
            priority = "high" if priority != "high" else priority
        if r.python and (r.python.radon_cc_max or r.python.max_function_cc) >= 20:
            reasons.append("high-function-complexity")
            priority = "high" if priority != "high" else priority
        if r.role in PRODUCTION_ROLES and r.lines.code_lines >= 500:
            reasons.append("large-production-file")
        if r.git.tracked and r.role in {"documentation", "asset", "data"} and r.top_level_dir not in {"docs", "ontology", "templates", "tests", "src", "tools"}:
            reasons.append("tracked-non-core-artifact")

        if reasons:
            finding = {
                "path": r.path,
                "role": r.role,
                "language": r.language,
                "tracked": r.git.tracked,
                "code_lines": r.lines.code_lines,
                "doc_lines": r.lines.doc_lines,
                "churn": r.git.churn,
                "risk_score": r.risk_score,
                "priority": priority,
                "reasons": "; ".join(dict.fromkeys(reasons)),
                "recommendation": recommendation,
            }
            findings.append(finding)

    findings.sort(key=lambda x: ({"high": 0, "medium": 1, "low": 2}.get(x["priority"], 9), -float(x["risk_score"]), -int(x["churn"]), x["path"]))
    return findings


def build_phase0_actions_md(repo_root: Path, args: argparse.Namespace, repo_info: dict[str, Any], records: list[FileRecord], issues: list[dict[str, Any]], policy_findings: list[dict[str, Any]], radon_any: bool, coverage_available: bool) -> str:
    tracked_backup = [f for f in policy_findings if "tracked-backup-file" in f["reasons"]]
    tracked_generated = [f for f in policy_findings if "tracked-generated-data" in f["reasons"]]
    high_hotspots = sorted(
        [r for r in records if r.role in ENGINEERING_ROLES and r.is_text],
        key=lambda x: (-x.hotspot_score, x.path),
    )[:10]

    top_hotspots = [
        {
            "path": r.path,
            "role": r.role,
            "code_lines": r.lines.code_lines,
            "churn": r.git.churn,
            "risk_score": round(r.risk_score, 2),
            "hotspot_score": round(r.hotspot_score, 2),
        }
        for r in high_hotspots
    ]

    lines = [
        "# Phase 0 Actions",
        "",
        f"Repository: `{repo_root}`  ",
        f"Branch: `{repo_info.get('branch')}`  ",
        f"HEAD: `{repo_info.get('head_sha')}`  ",
        f"Scan mode: `{args.scan_mode}`",
        "",
        "## Immediate Actions",
        "",
    ]

    if not coverage_available:
        lines.append("1. **Add coverage to the canonical metrics run.** Coverage is currently unavailable, so risk scoring lacks execution evidence.")
    else:
        lines.append("1. **Keep coverage in the canonical metrics run.**")
    if not radon_any:
        lines.append("2. **Install or enable `radon`.** The current run has no Radon MI/CC enrichment.")
    else:
        lines.append("2. **Radon is available. Keep it enabled in the canonical run.**")
    if tracked_backup:
        lines.append(f"3. **Remove tracked backup files** ({len(tracked_backup)} found).")
    else:
        lines.append("3. **No tracked backup files were detected.**")
    if tracked_generated:
        lines.append(f"4. **Decide what to do with tracked generated/export artifacts** ({len(tracked_generated)} found).")
    else:
        lines.append("4. **No tracked generated/export artifacts were detected.**")

    lines += [
        "",
        "## Tracked Backup Files",
        "",
    ]
    if tracked_backup:
        for row in tracked_backup[:20]:
            lines.append(f"- `{row['path']}` — {row['reasons']}")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Tracked Generated / Export Candidates",
        "",
    ]
    if tracked_generated:
        for row in tracked_generated[:20]:
            lines.append(f"- `{row['path']}` — {row['reasons']}")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Engineering Hotspots To Watch",
        "",
        "| File | Role | Code LOC | Churn | Risk | Hotspot |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in top_hotspots:
        lines.append(f"| `{row['path']}` | {row['role']} | {row['code_lines']} | {row['churn']} | {row['risk_score']:.2f} | {row['hotspot_score']:.2f} |")

    lines += [
        "",
        "## Suggested Commands",
        "",
        "```powershell",
        ".\.venv\Scripts\Activate.ps1",
        "pip install radon coverage pytest pytest-cov",
        "python .\tools\repo_metrics_bold.py . --scan-mode tracked --run-tests --pytest-target tests --coverage-target src",
        "```",
        "",
    ]

    return "\n".join(lines) + "\n"


def build_issue_rows(records: list[FileRecord], exact_dupes: list[dict[str, Any]], shadow_dupes: list[dict[str, Any]], coverage_available: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    python_present = any(r.language == "Python" for r in records)
    radon_any = any(r.python and r.python.radon_available for r in records if r.python)

    if not coverage_available:
        rows.append({
            "severity": "warning",
            "kind": "coverage-unavailable",
            "path": "",
            "details": "No coverage.json provided and --run-tests was not used."
        })
    if python_present and not radon_any:
        rows.append({
            "severity": "warning",
            "kind": "radon-unavailable",
            "path": "",
            "details": "Radon was not available in the run; MI/CC enrichment is partial."
        })

    for r in records:
        rel = Path(r.path)
        if r.python and r.python.syntax_error:
            rows.append({
                "severity": "error",
                "kind": "python-parse-error",
                "path": r.path,
                "details": r.python.syntax_error,
            })
        if r.role in PRODUCTION_ROLES and r.lines.code_lines >= 500:
            rows.append({
                "severity": "warning",
                "kind": "large-production-file",
                "path": r.path,
                "details": f"Production file has {r.lines.code_lines} code lines.",
            })
        if r.python and r.role in PRODUCTION_ROLES and (r.python.radon_cc_max or r.python.max_function_cc) >= 20:
            rows.append({
                "severity": "warning",
                "kind": "high-function-complexity",
                "path": r.path,
                "details": f"Max function CC is {r.python.radon_cc_max or r.python.max_function_cc}.",
            })
        if r.role in PRODUCTION_ROLES and r.git.churn >= 250:
            rows.append({
                "severity": "warning",
                "kind": "high-churn",
                "path": r.path,
                "details": f"Git churn is {r.git.churn}.",
            })
        if coverage_available and r.role in PRODUCTION_ROLES and r.coverage.statements > 0 and r.coverage.percent_covered < 70:
            rows.append({
                "severity": "warning",
                "kind": "low-coverage",
                "path": r.path,
                "details": f"Coverage is {r.coverage.percent_covered:.2f}%.",
            })
        if r.git.tracked and is_backup_like(rel):
            rows.append({
                "severity": "warning",
                "kind": "tracked-backup-file",
                "path": r.path,
                "details": "Tracked backup-like file should usually not live in the canonical repository.",
            })
        if r.git.tracked and is_staging_like(rel):
            rows.append({
                "severity": "warning",
                "kind": "tracked-staging-file",
                "path": r.path,
                "details": "Tracked staging/snapshot file should usually be removed from the canonical repository.",
            })
        if r.git.tracked and is_generated_data_like(rel, r.role):
            rows.append({
                "severity": "warning",
                "kind": "tracked-generated-data",
                "path": r.path,
                "details": "Tracked generated/export-style artifact should be reviewed for relocation or ignoring.",
            })

    for dup in exact_dupes[:50]:
        rows.append({
            "severity": "info",
            "kind": "exact-duplicate-text-group",
            "path": "",
            "details": dup["paths"],
        })
    for dup in shadow_dupes[:50]:
        rows.append({
            "severity": "warning",
            "kind": "shadow-duplicate",
            "path": dup["shadow_path"],
            "details": f"Mirrors {dup['source_path']}",
        })

    severity_order = {"error": 0, "warning": 1, "info": 2}
    rows.sort(key=lambda x: (severity_order.get(x["severity"], 9), x["kind"], x["path"]))
    return rows


# -----------------------------
# Flattening / reporting helpers
# -----------------------------
def flatten_file_record(r: FileRecord) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": r.path,
        "name": r.name,
        "extension": r.extension,
        "language": r.language,
        "role": r.role,
        "top_level_dir": r.top_level_dir,
        "size_bytes": r.size_bytes,
        "is_binary": r.is_binary,
        "is_text": r.is_text,
        "total_lines": r.lines.total_lines,
        "code_lines": r.lines.code_lines,
        "comment_lines": r.lines.comment_lines,
        "blank_lines": r.lines.blank_lines,
        "doc_lines": r.lines.doc_lines,
        "tracked": r.git.tracked,
        "visible_to_git": r.git.visible_to_git,
        "commit_count": r.git.commit_count,
        "additions": r.git.additions,
        "deletions": r.git.deletions,
        "churn": r.git.churn,
        "author_count": len(r.git.authors),
        "authors": "; ".join(r.git.authors),
        "last_commit_iso": r.git.last_commit_iso,
        "coverage_percent": r.coverage.percent_covered,
        "coverage_statements": r.coverage.statements,
        "coverage_branches": r.coverage.branches,
        "coverage_partial_branches": r.coverage.partial_branches,
        "risk_score": r.risk_score,
        "risk_label": risk_label(r.risk_score),
        "hotspot_score": r.hotspot_score,
        "size_bucket": classify_size_bucket(r.lines.code_lines),
        "content_sha1": r.content_sha1,
        "notes": "; ".join(r.notes),
    }
    if r.python:
        row |= {
            "module_name": r.python.module_name,
            "class_count": r.python.class_count,
            "function_count": r.python.function_count,
            "method_count": r.python.method_count,
            "test_function_count": r.python.test_function_count,
            "module_docstring": r.python.module_docstring,
            "docstring_lines": r.python.docstring_lines,
            "import_count": r.python.import_count,
            "internal_import_count": r.python.internal_import_count,
            "external_import_count": r.python.external_import_count,
            "average_function_length": r.python.average_function_length,
            "max_function_length": r.python.max_function_length,
            "average_function_cc": r.python.average_function_cc,
            "max_function_cc": r.python.max_function_cc,
            "average_max_nesting": r.python.average_max_nesting,
            "max_nesting": r.python.max_nesting,
            "approx_cyclomatic_complexity": r.python.approx_cyclomatic_complexity,
            "approx_halstead_volume": r.python.approx_halstead_volume,
            "approx_halstead_difficulty": r.python.approx_halstead_difficulty,
            "approx_halstead_effort": r.python.approx_halstead_effort,
            "approx_maintainability_index": r.python.approx_maintainability_index,
            "radon_available": r.python.radon_available,
            "radon_mi": r.python.radon_mi,
            "radon_cc_average": r.python.radon_cc_average,
            "radon_cc_max": r.python.radon_cc_max,
            "syntax_error": r.python.syntax_error,
            "internal_imports": "; ".join(r.python.imported_internal_modules),
            "external_imports": "; ".join(r.python.imported_external_modules),
        }
    return row


def markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    if not rows:
        return "_No data._"
    header = "| " + " | ".join(title for _, title in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        vals = []
        for key, _title in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                vals.append(f"{value:.2f}")
            else:
                vals.append(markdown_escape(value))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep, *body])


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    normalized_rows = [{key: row.get(key, "") for key in fieldnames} for row in rows]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_rows)


def build_markdown_report(
    repo_root: Path,
    args: argparse.Namespace,
    repo_info: dict[str, Any],
    coverage_summary: dict[str, Any],
    records: list[FileRecord],
    functions: list[PythonFunctionMetric],
    by_language: list[dict[str, Any]],
    by_role: list[dict[str, Any]],
    by_dir: list[dict[str, Any]],
    scope_rows: list[dict[str, Any]],
    exact_dupes: list[dict[str, Any]],
    shadow_dupes: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    top_n: int,
    radon_any: bool,
) -> str:
    text_files = [r for r in records if r.is_text]
    engineering_files = [r for r in records if r.role in ENGINEERING_ROLES]
    production_files = [r for r in records if r.role in PRODUCTION_ROLES]
    python_files = [r for r in records if r.language == "Python"]

    prod_lines = aggregate_lines(production_files)
    eng_lines = aggregate_lines(engineering_files)
    tracked_lines = aggregate_lines([r for r in records if r.git.tracked])

    top_engineering = sorted([flatten_file_record(r) for r in engineering_files if r.is_text], key=lambda x: (-x["code_lines"], x["path"]))[:top_n]
    top_hotspots = sorted([flatten_file_record(r) for r in engineering_files if r.is_text], key=lambda x: (-x["hotspot_score"], x["path"]))[:top_n]
    top_risky = sorted([flatten_file_record(r) for r in engineering_files if r.is_text], key=lambda x: (-x["risk_score"], x["path"]))[:top_n]

    low_mi = [flatten_file_record(r) for r in python_files if (r.python and (r.python.radon_mi or r.python.approx_maintainability_index) < 65)]
    low_mi = sorted(low_mi, key=lambda x: ((x.get("radon_mi") or x.get("approx_maintainability_index") or 0), x["path"]))[:top_n]
    complex_functions = sorted(
        [asdict(f) for f in functions],
        key=lambda x: (-x["cyclomatic_complexity"], -x["length"], x["qualified_name"])
    )[:top_n]

    issue_top = issues[:top_n]
    exact_top = exact_dupes[:top_n]
    shadow_top = shadow_dupes[:top_n]

    report = f"""# Repository Metrics Report v2

Generated: {utc_now_iso()}  
Repository: `{repo_root}`  
Scan mode: `{args.scan_mode}`  
Branch: `{repo_info.get('branch')}`  
HEAD: `{repo_info.get('head_sha')}`  
Git commits: {repo_info.get('commit_count', 0)}  
Coverage available: {coverage_summary.get('available', False)}  
Radon available in run: {radon_any}

## Executive Summary

- Files scanned: **{len(records)}**
- Git tracked files in repo: **{repo_info.get('tracked_files', 0)}**
- Git-visible files: **{repo_info.get('git_visible_files', 0)}**
- Text files scanned: **{sum(1 for r in records if r.is_text)}**
- Binary files scanned: **{sum(1 for r in records if r.is_binary)}**
- Engineering files: **{len(engineering_files)}**
- Production files: **{len(production_files)}**
- Python files: **{len(python_files)}**
- Tracked code lines: **{tracked_lines['code_lines']}**
- Engineering code lines: **{eng_lines['code_lines']}**
- Production code lines: **{prod_lines['code_lines']}**
- Engineering comment density: **{safe_div(eng_lines['comment_lines'], max(eng_lines['code_lines'] + eng_lines['comment_lines'], 1)):.2%}**
- Exact duplicate text groups: **{len(exact_dupes)}**
- Shadow duplicate pairs: **{len(shadow_dupes)}**
- Quality issues emitted: **{len(issues)}**
- Tracked backup-like files: **{sum(1 for r in records if r.git.tracked and is_backup_like(Path(r.path)))}**
- Tracked generated/export candidates: **{sum(1 for r in records if r.git.tracked and is_generated_data_like(Path(r.path), r.role))}**

## Scope Summary

{markdown_table(scope_rows, [("scope", "Scope"), ("file_count", "Files"), ("tracked_files", "Tracked"), ("code_lines", "Code LOC"), ("doc_lines", "Doc lines"), ("comment_lines", "Comments"), ("binary_files", "Binary"), ("total_churn", "Churn"), ("avg_risk_score", "Avg risk")])}

## Repo Mix by Role

{markdown_table(by_role, [("key", "Role"), ("file_count", "Files"), ("code_lines", "Code LOC"), ("doc_lines", "Doc lines"), ("comment_lines", "Comments"), ("total_churn", "Churn"), ("avg_risk_score", "Avg risk")])}

## Repo Mix by Language

{markdown_table(by_language, [("key", "Language"), ("file_count", "Files"), ("code_lines", "Code LOC"), ("comment_lines", "Comments"), ("doc_lines", "Doc lines"), ("total_churn", "Churn")])}

## Top-Level Directories

{markdown_table(by_dir, [("key", "Directory"), ("file_count", "Files"), ("code_lines", "Code LOC"), ("doc_lines", "Doc lines"), ("total_churn", "Churn"), ("avg_risk_score", "Avg risk"), ("avg_hotspot_score", "Avg hotspot")])}

## Largest Engineering Files by Code LOC

{markdown_table(top_engineering, [("path", "File"), ("language", "Lang"), ("role", "Role"), ("code_lines", "Code LOC"), ("comment_lines", "Comments"), ("churn", "Churn"), ("risk_score", "Risk")])}

## Top Hotspots (Engineering)

{markdown_table(top_hotspots, [("path", "File"), ("language", "Lang"), ("role", "Role"), ("hotspot_score", "Hotspot"), ("churn", "Churn"), ("average_function_cc", "Avg CC"), ("radon_mi", "Radon MI"), ("approx_maintainability_index", "Approx MI")])}

## Highest Risk Files (Engineering)

{markdown_table(top_risky, [("path", "File"), ("risk_label", "Risk"), ("risk_score", "Score"), ("code_lines", "Code LOC"), ("churn", "Churn"), ("coverage_percent", "Coverage %"), ("notes", "Flags")])}

## Lowest Maintainability Python Files

{markdown_table(low_mi, [("path", "File"), ("radon_mi", "Radon MI"), ("approx_maintainability_index", "Approx MI"), ("average_function_cc", "Avg CC"), ("max_function_cc", "Max CC"), ("max_function_length", "Max fn len")])}

## Most Complex Python Functions

{markdown_table(complex_functions, [("file", "File"), ("qualified_name", "Function"), ("cyclomatic_complexity", "CC"), ("max_nesting", "Max nesting"), ("length", "Length"), ("arg_count", "Args"), ("has_docstring", "Docstring")])}

## Quality Gates / Issues

{markdown_table(issue_top, [("severity", "Severity"), ("kind", "Kind"), ("path", "Path"), ("details", "Details")])}

## Exact Duplicate Text Groups

{markdown_table(exact_top, [("duplicate_count", "Count"), ("size_bytes", "Bytes"), ("sha1", "SHA1"), ("tracked_paths", "Tracked paths"), ("paths", "All paths")])}

## Shadow / Mirrored Duplicates

{markdown_table(shadow_top, [("source_path", "Source"), ("shadow_path", "Shadow"), ("size_bytes", "Bytes"), ("tracked_source", "Tracked src"), ("tracked_shadow", "Tracked shadow")])}

## Notes

- The script defaults to **Git-oriented scanning** (`auto -> tracked`) when `.git` is available. That prevents workspace logs, staging mirrors and untracked assets from inflating repo metrics.
- Python files are read with **UTF-8 BOM handling** (`utf-8-sig`) to avoid false parse errors from leading BOM bytes.
- Risk and hotspot scoring are **role-weighted**, so logs/assets/data no longer dominate engineering risk.
- The report now emits **phase-0 policy findings** for tracked backup files and tracked generated/export-style artifacts.
- When coverage is unavailable, the report emits an explicit quality warning instead of silently treating everything as uncovered.

## Suggested Next Moves

1. Use **`scan_mode=tracked`** as your canonical repo snapshot.
2. Run the canonical snapshot with **coverage + radon**.
3. Review **cleanup_candidates.csv** and **PHASE0_ACTIONS.md** before the next refactoring wave.
4. Remove tracked backup files and decide which generated/export artifacts should leave the canonical repo.
"""
    return report


# -----------------------------
# Main scan
# -----------------------------
def scan_repository(repo_root: Path, args: argparse.Namespace) -> tuple[list[FileRecord], list[PythonFunctionMetric], dict[str, Any], dict[str, Any]]:
    repo_info = git_head_info(repo_root)
    git_metrics = collect_git_file_metrics(repo_root) if args.with_git else {}
    rel_paths = collect_scan_rel_paths(repo_root, args)

    module_index: set[str] = set()
    for rel in rel_paths:
        if rel.suffix.lower() == ".py":
            mod = module_name_from_path(rel)
            if mod:
                module_index.add(mod)

    records: list[FileRecord] = []
    functions: list[PythonFunctionMetric] = []
    text_sha1_count = 0
    bom_python_files = 0

    for rel in rel_paths:
        path = repo_root / rel
        rel_posix = rel.as_posix()
        ext = path.suffix.lower()
        role = infer_role(rel)
        language = infer_language(path)

        binary = is_probably_binary(path)
        is_text = not binary
        lines = LineMetrics()
        content = None
        content_hash = None

        if is_text:
            try:
                content = read_text_normalized(path)
                lines = count_lines_from_text(content, role, ext)
                content_hash = sha1_text(content)
                text_sha1_count += 1
                if ext == ".py":
                    raw_bytes = path.read_bytes()[:3]
                    if raw_bytes.startswith(b"\xef\xbb\xbf"):
                        bom_python_files += 1
            except OSError:
                content = None

        gitm = git_metrics.get(rel_posix, GitMetrics(tracked=False, visible_to_git=False))
        record = FileRecord(
            path=rel_posix,
            name=path.name,
            extension=ext,
            language=language,
            role=role,
            top_level_dir=top_level_dir(rel),
            size_bytes=path.stat().st_size,
            is_binary=binary,
            is_text=is_text,
            lines=lines,
            git=gitm,
            coverage=CoverageMetrics(),
            content_sha1=content_hash,
        )

        if gitm.tracked and is_backup_like(rel):
            record.notes.append("tracked-backup-file")
        if gitm.tracked and is_staging_like(rel):
            record.notes.append("tracked-staging-file")
        if gitm.tracked and is_generated_data_like(rel, role):
            record.notes.append("tracked-generated-data")

        if ext == ".py" and is_text:
            pfm, file_functions = compute_python_metrics(path, rel, lines.code_lines, module_index, args.use_radon)
            record.python = pfm
            functions.extend(file_functions)
        records.append(record)

    scan_meta = {
        "module_index_size": len(module_index),
        "scan_mode_resolved": ("tracked" if args.scan_mode == "auto" and git_available(repo_root) else args.scan_mode),
        "text_sha1_count": text_sha1_count,
        "python_files_with_bom": bom_python_files,
    }
    return records, functions, repo_info, scan_meta


# -----------------------------
# Output / orchestration
# -----------------------------
def build_output_dir(repo_root: Path, user_out_dir: str | None) -> Path:
    if user_out_dir:
        out_dir = Path(user_out_dir)
        if not out_dir.is_absolute():
            out_dir = repo_root / out_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = repo_root / "docs" / "_metrics" / f"repo_metrics_v2_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Comprehensive repository metrics analyzer (phase-0 ready)")
    parser.add_argument("repo", nargs="?", default=".", help="Path to the repository root")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: docs/_metrics/repo_metrics_v2_<timestamp>)")
    parser.add_argument("--scan-mode", choices=["auto", "tracked", "git-visible", "filesystem"], default="auto",
                        help="What file universe to scan. auto=tracked if git exists, otherwise filesystem.")
    parser.add_argument("--top-n", type=int, default=20, help="Top N rows to show in Markdown report tables")
    parser.add_argument("--max-hotspots", type=int, default=50, help="Max hotspots / risky rows to persist in JSON")
    parser.add_argument("--run-tests", action="store_true", help="Run pytest with coverage before reporting")
    parser.add_argument("--pytest-target", default="tests", help="Pytest target path when --run-tests is used")
    parser.add_argument("--coverage-target", default="src", help="Coverage source target when --run-tests is used")
    parser.add_argument("--coverage-json", default=None, help="Existing coverage.json to ingest instead of running tests")
    parser.add_argument("--cov-context-tests", action="store_true", help="Use pytest-cov per-test contexts when running coverage")
    parser.add_argument("--pytest-extra", nargs="*", default=[], help="Extra arguments forwarded to pytest")
    parser.add_argument("--with-git", action="store_true", default=True, help="Include git metrics (default: on)")
    parser.add_argument("--without-git", dest="with_git", action="store_false", help="Disable git metrics")
    parser.add_argument("--use-radon", action="store_true", default=True, help="Use radon if installed (default: on)")
    parser.add_argument("--without-radon", dest="use_radon", action="store_false", help="Disable radon integration")
    parser.add_argument("--exclude", nargs="*", default=[], help="Additional directory/file names to exclude")
    parser.add_argument("--exclude-glob", nargs="*", default=[], help="Additional glob patterns to exclude")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        print(f"Repository path does not exist or is not a directory: {repo_root}", file=sys.stderr)
        return 2

    args.excludes = set(DEFAULT_EXCLUDES) | set(args.exclude)
    args.exclude_globs = set(DEFAULT_EXCLUDE_GLOBS) | set(args.exclude_glob)

    out_dir = build_output_dir(repo_root, args.out_dir)
    args.out_dir = out_dir

    records, functions, repo_info, scan_meta = scan_repository(repo_root, args)

    coverage_json_path: Path | None = None
    if args.coverage_json:
        coverage_json_path = Path(args.coverage_json)
        if not coverage_json_path.is_absolute():
            coverage_json_path = repo_root / coverage_json_path
    elif args.run_tests:
        coverage_json_path = maybe_run_pytest_coverage(repo_root, args, out_dir)

    coverage_by_file: dict[str, CoverageMetrics] = {}
    coverage_summary: dict[str, Any] = {"available": False}
    if coverage_json_path:
        coverage_by_file, coverage_summary = parse_coverage_json(coverage_json_path)

    # Merge coverage into file records.
    for r in records:
        if r.path in coverage_by_file:
            r.coverage = coverage_by_file[r.path]
        else:
            matches = [cm for fp, cm in coverage_by_file.items() if fp.endswith(r.path)]
            if matches:
                r.coverage = matches[0]

    compute_scores(records, coverage_available=bool(coverage_summary.get("available", False)))

    by_language = summarize_by(records, lambda r: r.language)
    by_role = summarize_by(records, lambda r: r.role)
    by_dir = summarize_by(records, lambda r: r.top_level_dir)

    flattened = [flatten_file_record(r) for r in records]
    flattened.sort(key=lambda x: x["path"])

    function_rows = [asdict(f) for f in functions]
    function_rows.sort(key=lambda x: (x["file"], x["lineno"], x["qualified_name"]))

    top_hotspots = sorted([r for r in flattened if r["role"] in ENGINEERING_ROLES], key=lambda x: (-x["hotspot_score"], x["path"]))[: args.max_hotspots]
    top_risky = sorted([r for r in flattened if r["role"] in ENGINEERING_ROLES], key=lambda x: (-x["risk_score"], x["path"]))[: args.max_hotspots]

    exact_dupes = detect_exact_duplicates(records)
    shadow_dupes = detect_shadow_duplicates(records)
    scope_rows = build_scope_rows(records)
    issues = build_issue_rows(records, exact_dupes, shadow_dupes, coverage_available=bool(coverage_summary.get("available", False)))
    policy_findings = collect_policy_findings(records, issues)

    radon_any = any(r.python and r.python.radon_available for r in records if r.python)

    summary = {
        "generated_at": utc_now_iso(),
        "repo_root": str(repo_root),
        "config": {
            "scan_mode": args.scan_mode,
            "excludes": sorted(args.excludes),
            "exclude_globs": sorted(args.exclude_globs),
            "with_git": args.with_git,
            "use_radon": args.use_radon,
            "run_tests": args.run_tests,
            "coverage_json": str(coverage_json_path) if coverage_json_path else None,
        },
        "repo": repo_info,
        "scan_meta": scan_meta,
        "tooling": {
            "git_available": git_available(repo_root),
            "radon_available_any": radon_any,
            "coverage_available": bool(coverage_summary.get("available", False)),
        },
        "coverage_summary": coverage_summary,
        "counts": {
            "files_total": len(records),
            "files_text": sum(1 for r in records if r.is_text),
            "files_binary": sum(1 for r in records if r.is_binary),
            "files_tracked": sum(1 for r in records if r.git.tracked),
            "files_git_visible": sum(1 for r in records if r.git.visible_to_git),
            "python_functions_total": len(functions),
            "exact_duplicate_groups": len(exact_dupes),
            "shadow_duplicate_pairs": len(shadow_dupes),
            "issues_total": len(issues),
        },
        "policy_summary": {
            "tracked_backup_files": sum(1 for r in records if r.git.tracked and is_backup_like(Path(r.path))),
            "tracked_generated_data_candidates": sum(1 for r in records if r.git.tracked and is_generated_data_like(Path(r.path), r.role)),
            "cleanup_candidates_total": len(policy_findings),
        },
        "line_totals": aggregate_lines(records),
        "scopes": scope_rows,
        "by_language": by_language,
        "by_role": by_role,
        "by_top_level_dir": by_dir,
        "top_hotspots": top_hotspots,
        "top_risky": top_risky,
    }

    json_payload = {
        "summary": summary,
        "files": flattened,
        "functions": function_rows,
        "duplicates": {
            "exact_groups": exact_dupes,
            "shadow_pairs": shadow_dupes,
        },
        "issues": issues,
        "policy_findings": policy_findings,
    }

    # Write outputs
    (out_dir / "repo_metrics_v2.json").write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(out_dir / "files.csv", flattened)
    write_csv(out_dir / "functions.csv", function_rows)
    write_csv(out_dir / "languages.csv", by_language)
    write_csv(out_dir / "roles.csv", by_role)
    write_csv(out_dir / "directories.csv", by_dir)
    write_csv(out_dir / "scopes.csv", scope_rows)
    write_csv(out_dir / "hotspots.csv", top_hotspots)
    write_csv(out_dir / "risky_files.csv", top_risky)
    write_csv(out_dir / "duplicates_exact.csv", exact_dupes)
    write_csv(out_dir / "duplicates_shadow.csv", shadow_dupes)
    write_csv(out_dir / "issues.csv", issues)
    write_csv(out_dir / "cleanup_candidates.csv", policy_findings)

    report = build_markdown_report(
        repo_root=repo_root,
        args=args,
        repo_info=repo_info,
        coverage_summary=coverage_summary,
        records=records,
        functions=functions,
        by_language=by_language,
        by_role=by_role,
        by_dir=by_dir,
        scope_rows=scope_rows,
        exact_dupes=exact_dupes,
        shadow_dupes=shadow_dupes,
        issues=issues,
        top_n=args.top_n,
        radon_any=radon_any,
    )
    (out_dir / "REPORT_v2.md").write_text(report, encoding="utf-8")
    phase0_actions = build_phase0_actions_md(
        repo_root=repo_root,
        args=args,
        repo_info=repo_info,
        records=records,
        issues=issues,
        policy_findings=policy_findings,
        radon_any=radon_any,
        coverage_available=bool(coverage_summary.get("available", False)),
    )
    (out_dir / "PHASE0_ACTIONS.md").write_text(phase0_actions, encoding="utf-8")

    manifest = {
        "out_dir": str(out_dir),
        "generated_at": utc_now_iso(),
        "artifacts": [
            "repo_metrics_v2.json",
            "REPORT_v2.md",
            "PHASE0_ACTIONS.md",
            "files.csv",
            "functions.csv",
            "languages.csv",
            "roles.csv",
            "directories.csv",
            "scopes.csv",
            "hotspots.csv",
            "risky_files.csv",
            "duplicates_exact.csv",
            "duplicates_shadow.csv",
            "issues.csv",
            "cleanup_candidates.csv",
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Repository metrics v2 written to: {out_dir}")
    print("Artifacts:")
    for name in manifest["artifacts"]:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

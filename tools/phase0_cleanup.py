#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

BACKUP_SUFFIXES = {".bak", ".orig", ".old", ".tmp", ".backup"}
TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".html", ".htm", ".ini",
    ".cfg", ".toml", ".ps1", ".bat", ".sh", ".sql", ".csv", ".env", ".example",
    ".sample", ".gitignore", ".gitattributes", ".code-workspace",
}
GENERATED_HINTS = [
    "export", "snapshot", "dump", "report", "metrics", "handoff", "audit",
]


@dataclass
class FileFinding:
    path: str
    reason: str
    detail: str = ""


def run_git(repo_root: Path, *args: str) -> str:
    cmd = ["git", "-C", str(repo_root), *args]
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")


def tracked_files(repo_root: Path) -> list[Path]:
    out = run_git(repo_root, "ls-files")
    return [repo_root / line.strip() for line in out.splitlines() if line.strip()]


def is_likely_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name.startswith(".") and path.suffix == "":
        return True
    return False


def detect_bom(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


def strip_bom(path: Path) -> bool:
    raw = path.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        return False
    path.write_bytes(raw[3:])
    return True


def find_backup_files(paths: Iterable[Path], repo_root: Path) -> list[FileFinding]:
    findings: list[FileFinding] = []
    for p in paths:
        name = p.name.lower()
        if p.suffix.lower() in BACKUP_SUFFIXES or name.endswith("~"):
            findings.append(FileFinding(str(p.relative_to(repo_root)), "tracked_backup_file"))
    return findings


def find_generated_candidates(paths: Iterable[Path], repo_root: Path) -> list[FileFinding]:
    findings: list[FileFinding] = []
    for p in paths:
        low = p.name.lower()
        if any(h in low for h in GENERATED_HINTS):
            # keep obvious source code out, focus on likely data/artifact-style files
            if p.suffix.lower() in {".json", ".csv", ".md"} and "repo_metrics_bold" not in low:
                findings.append(FileFinding(str(p.relative_to(repo_root)), "generated_or_export_candidate"))
    return findings


def find_bom_files(paths: Iterable[Path], repo_root: Path) -> list[FileFinding]:
    findings: list[FileFinding] = []
    for p in paths:
        if not is_likely_text(p):
            continue
        if detect_bom(p):
            findings.append(FileFinding(str(p.relative_to(repo_root)), "utf8_bom"))
    return findings


def render_md(repo_root: Path, backups: list[FileFinding], generated: list[FileFinding], boms: list[FileFinding]) -> str:
    lines = []
    lines.append("# Phase 0 Cleanup Report")
    lines.append("")
    lines.append(f"Repository: `{repo_root}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Tracked backup-like files: **{len(backups)}**")
    lines.append(f"- Tracked generated/export candidates: **{len(generated)}**")
    lines.append(f"- UTF-8 BOM text files: **{len(boms)}**")
    lines.append("")
    if backups:
        lines.append("## Backup-like Files")
        lines.append("")
        for f in backups:
            lines.append(f"- `{f.path}`")
        lines.append("")
        lines.append("Suggested command:")
        lines.append("")
        for f in backups:
            lines.append(f"- `git rm -- \"{f.path}\"`")
        lines.append("")
    if generated:
        lines.append("## Generated / Export Candidates")
        lines.append("")
        lines.append("Review manually before removal. Keep only if they are canonical source data.")
        lines.append("")
        for f in generated:
            lines.append(f"- `{f.path}`")
        lines.append("")
        lines.append("Possible command for non-canonical artifacts:")
        lines.append("")
        for f in generated:
            lines.append(f"- `git rm --cached \"{f.path}\"`")
        lines.append("")
    if boms:
        lines.append("## UTF-8 BOM Files")
        lines.append("")
        lines.append("These files start with a BOM. For Python files this can create noisy parsing/tooling issues.")
        lines.append("")
        for f in boms:
            lines.append(f"- `{f.path}`")
        lines.append("")
        lines.append("Dry run fix:")
        lines.append("")
        lines.append("- `python .\\tools\\phase0_cleanup.py .`")
        lines.append("")
        lines.append("Apply BOM removal:")
        lines.append("")
        lines.append("- `python .\\tools\\phase0_cleanup.py . --strip-bom`")
        lines.append("")
    lines.append("## Recommended Order")
    lines.append("")
    lines.append("1. Remove tracked backup-like files.")
    lines.append("2. Decide whether tracked export/generated artifacts are canonical or should leave Git.")
    lines.append("3. Strip BOM from tracked text files, then rerun metrics and tests.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 0 cleanup helper for tracked repo files.")
    ap.add_argument("repo_root", nargs="?", default=".")
    ap.add_argument("--strip-bom", action="store_true", help="Remove UTF-8 BOM from tracked text files in place.")
    ap.add_argument("--output-dir", default=None, help="Directory for JSON/MD report. Defaults to repo root / docs/_metrics/phase0_cleanup_latest")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    tracked = tracked_files(repo_root)

    backups = find_backup_files(tracked, repo_root)
    generated = find_generated_candidates(tracked, repo_root)
    boms = find_bom_files(tracked, repo_root)

    stripped = []
    if args.strip_bom:
        for item in boms:
            p = repo_root / item.path
            if strip_bom(p):
                stripped.append(item.path)

    out_dir = Path(args.output_dir) if args.output_dir else (repo_root / "docs" / "_metrics" / "phase0_cleanup_latest")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "repo_root": str(repo_root),
        "tracked_files": len(tracked),
        "tracked_backup_files": [asdict(x) for x in backups],
        "tracked_generated_candidates": [asdict(x) for x in generated],
        "utf8_bom_files": [asdict(x) for x in boms],
        "bom_stripped": stripped,
    }
    (out_dir / "phase0_cleanup.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "PHASE0_ACTIONS.md").write_text(render_md(repo_root, backups, generated, boms), encoding="utf-8")

    print(f"Phase 0 cleanup report written to: {out_dir}")
    print("Artifacts:")
    print("- phase0_cleanup.json")
    print("- PHASE0_ACTIONS.md")
    if args.strip_bom:
        print(f"- BOM stripped in {len(stripped)} files")
    else:
        print(f"- BOM findings: {len(boms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
}

MAX_LIST_ITEMS = 100


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def utc_iso_from_ts(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).isoformat(timespec="seconds")


def human_bytes(num: int) -> str:
    value = float(num)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{num} B"


def run_git(root: Path, args: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return proc.returncode, out
    except Exception as exc:
        return 999, f"ERROR: {exc}"


def load_git_sets(root: Path) -> Tuple[Optional[set[str]], Optional[set[str]], Optional[set[str]]]:
    rc, tracked_out = run_git(root, ["ls-files", "-z"])
    if rc != 0:
        return None, None, None
    tracked = {p for p in tracked_out.split("\0") if p}

    rc, untracked_out = run_git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    if rc != 0:
        return tracked, None, None
    untracked = {p for p in untracked_out.split("\0") if p}

    rc, ignored_out = run_git(root, ["ls-files", "--others", "-i", "--exclude-standard", "-z"])
    if rc != 0:
        return tracked, untracked, None
    ignored = {p for p in ignored_out.split("\0") if p}
    return tracked, untracked, ignored


def classify_git_state(rel_posix: str, tracked: Optional[set[str]], untracked: Optional[set[str]], ignored: Optional[set[str]]) -> str:
    if tracked is None:
        return "unknown"
    if rel_posix in tracked:
        return "tracked"
    if ignored is not None and rel_posix in ignored:
        return "ignored"
    if untracked is not None and rel_posix in untracked:
        return "untracked"
    return "filesystem_only"


def top_scope(rel: Path) -> str:
    parts = rel.parts
    return parts[0] if parts else "."


def suggest_action(rel_posix: str, git_state: str, is_dir: bool, size_bytes: int) -> Tuple[str, str]:
    rel_lower = rel_posix.lower()
    parts = rel_posix.split("/")

    if rel_lower.startswith("logs/"):
        return "review_delete", "operatives Logfile/Log-Verzeichnis"
    if rel_lower.startswith("docs/_snapshot/"):
        return "review_archive_or_delete", "generierter Snapshot/Handoff-Output"
    if rel_lower.startswith("docs/_ops/"):
        return "review_archive_or_delete", "operatives Laufartefakt/Report-Output"
    if rel_lower.startswith("docs/_metrics/"):
        return "review_archive_or_delete", "generierter Metrics-Output"
    if rel_lower.startswith("docs/_notebooklm/"):
        return "review_archive_or_delete", "Hilfs-/Exportmaterial außerhalb Kerndoku"
    if rel_lower.startswith("dist/") or rel_lower.startswith("build/") or rel_lower.startswith("_release_staging/"):
        return "review_delete", "Build-/Staging-Artefakt"
    if rel_lower.endswith((".tmp", ".bak", ".orig", ".rej")) or rel_lower.endswith("~"):
        return "review_delete", "Backup-/Temp-Datei"
    if rel_lower.endswith(".zip") and len(parts) == 1:
        return "review_archive_or_delete", "Root-Zip/Export im Arbeitsverzeichnis"
    if len(parts) == 1 and rel_lower.endswith((".md", ".txt", ".ps1")) and git_state != "tracked":
        return "review_archive", "lose Arbeits-/Notizdatei im Repo-Root"
    if len(parts) == 1 and rel_lower.endswith((".md", ".txt")) and git_state == "tracked":
        return "review_keep_or_archive", "versionierte Root-Dokumentation prüfen"
    if is_dir and rel_lower in {"logs", "docs/_ops", "docs/_snapshot", "docs/_metrics"}:
        return "review_archive_or_delete", "generiertes Verzeichnis"
    if git_state == "untracked":
        return "review_now", "untracked Datei/Ordner im Workspace"
    if size_bytes >= 50 * 1024 * 1024:
        return "review_large", "große Datei"
    return "keep", "keine offensichtliche Aufräumauffälligkeit"


def should_skip_dir(name: str) -> bool:
    return name in DEFAULT_SKIP_DIRS


def iter_entries(root: Path) -> Iterable[Tuple[Path, os.stat_result, bool]]:
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted([d for d in dirnames if not should_skip_dir(d)])
        current = Path(current_root)
        for dirname in dirnames:
            path = current / dirname
            try:
                stat = path.stat()
            except OSError:
                continue
            yield path, stat, True
        for filename in sorted(filenames):
            path = current / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            yield path, stat, False


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def md_table(headers: List[str], rows: List[List[str]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def build_summary(
    root: Path,
    out_dir: Path,
    entries: List[Dict[str, object]],
    dir_rows: List[Dict[str, object]],
    tracked: Optional[set[str]],
) -> str:
    files = [x for x in entries if x["kind"] == "file"]
    dirs = [x for x in entries if x["kind"] == "dir"]
    total_bytes = sum(int(x["size_bytes"]) for x in files)
    by_git = Counter(str(x["git_state"]) for x in entries)
    by_action = Counter(str(x["suggested_action"]) for x in entries)
    by_top = defaultdict(lambda: {"files": 0, "dirs": 0, "bytes": 0})
    for row in entries:
        top = str(row["top_scope"])
        if row["kind"] == "file":
            by_top[top]["files"] += 1
            by_top[top]["bytes"] += int(row["size_bytes"])
        else:
            by_top[top]["dirs"] += 1

    largest_files = sorted(files, key=lambda x: int(x["size_bytes"]), reverse=True)[:25]
    root_level = sorted([x for x in entries if str(x["relative_path"]).count("/") == 0], key=lambda x: (x["kind"], str(x["relative_path"])))
    candidate_rows = [x for x in entries if str(x["suggested_action"]) != "keep"]
    candidate_rows = sorted(candidate_rows, key=lambda x: (str(x["suggested_action"]), str(x["relative_path"])))[:100]

    docs_rows = [x for x in entries if str(x["relative_path"]).startswith("docs/")]
    logs_rows = [x for x in entries if str(x["relative_path"]).startswith("logs/")]

    lines: List[str] = []
    lines.append("# Workspace Inventory Summary")
    lines.append("")
    lines.append(f"- generated_local: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- repo_root: `{root}`")
    lines.append(f"- output_dir: `{out_dir}`")
    lines.append(f"- git_available: `{'yes' if tracked is not None else 'no'}`")
    lines.append("")
    lines.append("## Gesamtbild")
    lines.append("")
    lines.append(md_table(
        ["Metrik", "Wert"],
        [
            ["Dateien", str(len(files))],
            ["Ordner", str(len(dirs))],
            ["Gesamtgröße Dateien", human_bytes(total_bytes)],
            ["Git tracked", str(by_git.get("tracked", 0))],
            ["Git untracked", str(by_git.get("untracked", 0))],
            ["Git ignored", str(by_git.get("ignored", 0))],
            ["Nicht klar klassifiziert", str(by_git.get("filesystem_only", 0) + by_git.get("unknown", 0))],
            ["Cleanup-/Review-Kandidaten", str(len([x for x in entries if str(x["suggested_action"]) != "keep"]))],
        ],
    ))
    lines.append("")
    lines.append("## Top-Level-Bereiche")
    lines.append("")
    top_rows = []
    for top, payload in sorted(by_top.items(), key=lambda kv: kv[0].lower()):
        top_rows.append([top, str(payload["dirs"]), str(payload["files"]), human_bytes(int(payload["bytes"]))])
    lines.append(md_table(["Bereich", "Ordner", "Dateien", "Dateigröße"], top_rows or [["(leer)", "0", "0", "0 B"]]))
    lines.append("")
    lines.append("## Root-Dateien und Root-Ordner")
    lines.append("")
    rr = []
    for row in root_level[:100]:
        rr.append([
            str(row["relative_path"]),
            str(row["kind"]),
            str(row["git_state"]),
            str(row["suggested_action"]),
            human_bytes(int(row["size_bytes"])) if row["kind"] == "file" else "-",
        ])
    lines.append(md_table(["Pfad", "Art", "Git", "Empfehlung", "Größe"], rr or [["(keine)", "-", "-", "-", "-"]]))
    lines.append("")
    lines.append("## docs/ und logs/ Schnellblick")
    lines.append("")
    lines.append(md_table(
        ["Bereich", "Dateien", "Ordner", "Dateigröße"],
        [
            [
                "docs/",
                str(sum(1 for x in docs_rows if x["kind"] == "file")),
                str(sum(1 for x in docs_rows if x["kind"] == "dir")),
                human_bytes(sum(int(x["size_bytes"]) for x in docs_rows if x["kind"] == "file")),
            ],
            [
                "logs/",
                str(sum(1 for x in logs_rows if x["kind"] == "file")),
                str(sum(1 for x in logs_rows if x["kind"] == "dir")),
                human_bytes(sum(int(x["size_bytes"]) for x in logs_rows if x["kind"] == "file")),
            ],
        ],
    ))
    lines.append("")
    lines.append("## Größte Dateien (Top 25)")
    lines.append("")
    lf = []
    for row in largest_files:
        lf.append([
            str(row["relative_path"]),
            human_bytes(int(row["size_bytes"])),
            str(row["git_state"]),
            str(row["suggested_action"]),
        ])
    lines.append(md_table(["Pfad", "Größe", "Git", "Empfehlung"], lf or [["(keine)", "-", "-", "-"]]))
    lines.append("")
    lines.append("## Aufräum-/Archiv-Kandidaten (Top 100)")
    lines.append("")
    cr = []
    for row in candidate_rows:
        cr.append([
            str(row["relative_path"]),
            str(row["kind"]),
            str(row["git_state"]),
            str(row["suggested_action"]),
            str(row["reason"]),
        ])
    lines.append(md_table(["Pfad", "Art", "Git", "Empfehlung", "Grund"], cr or [["(keine)", "-", "-", "-", "-"]]))
    lines.append("")
    lines.append("## Empfohlener nächster Schritt")
    lines.append("")
    lines.append("1. `cleanup_candidates.csv` prüfen.")
    lines.append("2. Root-Dateien, `logs/`, `docs/_ops/`, `docs/_snapshot/`, `docs/_metrics/` getrennt entscheiden.")
    lines.append("3. Erst danach ein dediziertes Move/Delete-Skript bauen.")
    lines.append("")
    return "\n".join(lines) + "\n"


def top_tree(root: Path, max_depth: int = 3) -> str:
    lines: List[str] = []
    lines.append(str(root))
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        rel = current.relative_to(root)
        depth = len(rel.parts)
        if depth >= max_depth:
            dirnames[:] = []
        dirnames[:] = sorted([d for d in dirnames if not should_skip_dir(d)])
        indent = "    " * depth
        for dirname in dirnames:
            lines.append(f"{indent}[D] {dirname}")
        for filename in sorted(filenames):
            lines.append(f"{indent}[F] {filename}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a local workspace inventory for cleanup planning.")
    ap.add_argument("--root", default=".", help="Repo/workspace root")
    ap.add_argument("--out-dir", default="", help="Explicit output dir. Default: docs/_ops/workspace_inventory/run_<timestamp>")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else (root / "docs" / "_ops" / "workspace_inventory" / f"run_{now_stamp()}")
    out_dir.mkdir(parents=True, exist_ok=True)

    tracked, untracked, ignored = load_git_sets(root)

    entries: List[Dict[str, object]] = []
    dir_acc = defaultdict(lambda: {"direct_files": 0, "direct_dirs": 0, "direct_bytes": 0})

    for path, stat, is_dir in iter_entries(root):
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        git_state = classify_git_state(rel_posix, tracked, untracked, ignored)
        size_bytes = 0 if is_dir else int(stat.st_size)
        action, reason = suggest_action(rel_posix, git_state, is_dir, size_bytes)

        row = {
            "relative_path": rel_posix,
            "kind": "dir" if is_dir else "file",
            "top_scope": top_scope(rel),
            "git_state": git_state,
            "size_bytes": size_bytes,
            "mtime_utc": utc_iso_from_ts(stat.st_mtime),
            "suggested_action": action,
            "reason": reason,
            "suffix": path.suffix.lower(),
        }
        entries.append(row)

        parent_key = rel.parent.as_posix() if rel.parent.as_posix() != "." else "."
        if is_dir:
            dir_acc[parent_key]["direct_dirs"] += 1
        else:
            dir_acc[parent_key]["direct_files"] += 1
            dir_acc[parent_key]["direct_bytes"] += size_bytes

    dir_rows: List[Dict[str, object]] = []
    for entry in sorted([x for x in entries if x["kind"] == "dir"], key=lambda x: str(x["relative_path"])):
        key = str(entry["relative_path"])
        payload = dir_acc.get(key, {})
        dir_rows.append({
            "relative_path": key,
            "top_scope": str(entry["top_scope"]),
            "git_state": str(entry["git_state"]),
            "direct_child_dirs": int(payload.get("direct_dirs", 0)),
            "direct_child_files": int(payload.get("direct_files", 0)),
            "direct_child_bytes": int(payload.get("direct_bytes", 0)),
            "mtime_utc": str(entry["mtime_utc"]),
            "suggested_action": str(entry["suggested_action"]),
            "reason": str(entry["reason"]),
        })

    file_rows = sorted(entries, key=lambda x: (str(x["relative_path"])))
    candidate_rows = [x for x in file_rows if str(x["suggested_action"]) != "keep"]
    summary_md = build_summary(root, out_dir, file_rows, dir_rows, tracked)
    tree_txt = top_tree(root, max_depth=3)

    write_csv(
        out_dir / "inventory_files.csv",
        file_rows,
        ["relative_path", "kind", "top_scope", "git_state", "size_bytes", "mtime_utc", "suggested_action", "reason", "suffix"],
    )
    write_csv(
        out_dir / "inventory_dirs.csv",
        dir_rows,
        ["relative_path", "top_scope", "git_state", "direct_child_dirs", "direct_child_files", "direct_child_bytes", "mtime_utc", "suggested_action", "reason"],
    )
    write_csv(
        out_dir / "cleanup_candidates.csv",
        candidate_rows,
        ["relative_path", "kind", "top_scope", "git_state", "size_bytes", "mtime_utc", "suggested_action", "reason", "suffix"],
    )

    payload = {
        "generated_local": dt.datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(root),
        "git_available": tracked is not None,
        "counts": {
            "entries": len(file_rows),
            "files": sum(1 for x in file_rows if x["kind"] == "file"),
            "dirs": sum(1 for x in file_rows if x["kind"] == "dir"),
            "tracked": sum(1 for x in file_rows if x["git_state"] == "tracked"),
            "untracked": sum(1 for x in file_rows if x["git_state"] == "untracked"),
            "ignored": sum(1 for x in file_rows if x["git_state"] == "ignored"),
            "candidates": len(candidate_rows),
        },
    }
    (out_dir / "inventory_summary.md").write_text(summary_md, encoding="utf-8", newline="\n")
    (out_dir / "inventory_tree_depth3.txt").write_text(tree_txt, encoding="utf-8", newline="\n")
    (out_dir / "inventory_manifest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] workspace inventory written to: {out_dir}")
    print("[ARTIFACTS]")
    print("- inventory_summary.md")
    print("- inventory_files.csv")
    print("- inventory_dirs.csv")
    print("- cleanup_candidates.csv")
    print("- inventory_tree_depth3.txt")
    print("- inventory_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

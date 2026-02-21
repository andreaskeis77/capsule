#!/usr/bin/env python3
"""
Handoff Master Script
Creates a full handoff bundle under docs/_snapshot/handoff_YYYYMMDD-HHMMSS
and updates docs/_snapshot/latest.

Steps:
1) sanity check (requires server running)
2) project audit dump
3) data snapshot
4) ontology runtime dump (json + md)
5) runtime state capture
6) handoff manifest instantiation + summary

Exit codes:
0 = success
2 = any step failed
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(cmd: List[str], cwd: Path) -> Tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
        out = (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")
        return r.returncode, out.strip()
    except Exception as e:
        return 999, f"ERROR running {cmd}: {e}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--base", default="http://127.0.0.1:5002", help="Server base url (server must be running)")
    ap.add_argument("--user", default="karen", help="User for sanity check urls")
    ap.add_argument("--ids", default="112,101,110", help="IDs for selection sanity check")
    ap.add_argument("--max-bytes", type=int, default=1_000_000, help="Max bytes per file in audit dump")
    ap.add_argument("--include-ontology-text", action="store_true",
                    help="Include ontology_part_*.md text inside ontology_runtime_dump.json (default: off)")
    ap.add_argument("--ontology-max-chars", type=int, default=250_000,
                    help="Max chars per ontology MD part when included (default: 250000)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    snap_root = root / "docs" / "_snapshot"
    stamp = now_stamp()
    out_dir = snap_root / f"handoff_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = []
    failed = False

    # 0) git metadata (best effort)
    rc, head = run(["git", "rev-parse", "HEAD"], cwd=root)
    git_head = head.splitlines()[-1].strip() if rc == 0 and head else "unknown"
    rc, br = run(["git", "branch", "--show-current"], cwd=root)
    git_branch = br.strip() if rc == 0 and br else "unknown"

    # 1) sanity check (server running)
    sanity_out = out_dir / "sanity_check.txt"
    rc, out = run(
        [sys.executable, "tools/project_sanity_check.py", "--base", args.base, "--user", args.user, "--ids", args.ids],
        cwd=root,
    )
    write_text(sanity_out, out + "\n")
    steps.append(("sanity_check", rc, str(sanity_out)))
    if rc != 0:
        failed = True

    # 2) project audit dump
    audit_out = out_dir / "project_audit_dump.md"
    rc, out = run(
        [
            sys.executable, "tools/project_audit_dump.py",
            "--root", ".",
            "--out", str(audit_out),
            "--max-bytes", str(args.max_bytes),
        ],
        cwd=root,
    )
    steps.append(("project_audit_dump", rc, str(audit_out)))
    if rc != 0:
        failed = True
        write_text(out_dir / "project_audit_dump.stderr.txt", out + "\n")

    # 3) data snapshot
    data_out = out_dir / "data_snapshot.md"
    rc, out = run(
        [sys.executable, "tools/project_data_snapshot.py", "--root", ".", "--out", str(data_out)],
        cwd=root,
    )
    steps.append(("project_data_snapshot", rc, str(data_out)))
    if rc != 0:
        failed = True
        write_text(out_dir / "data_snapshot.stderr.txt", out + "\n")

    # 4) ontology runtime dump
    onto_json = out_dir / "ontology_runtime_dump.json"
    onto_md = out_dir / "ontology_runtime_summary.md"
    cmd = [
        sys.executable, "tools/ontology_runtime_dump.py",
        "--root", ".",
        "--out-json", str(onto_json),
        "--out-md", str(onto_md),
        "--max-part-chars", str(args.ontology_max_chars),
    ]
    if args.include_ontology_text:
        cmd.append("--include-part-text")

    rc, out = run(cmd, cwd=root)
    steps.append(("ontology_runtime_dump", rc, f"{onto_json} / {onto_md}"))
    if rc != 0:
        failed = True
        write_text(out_dir / "ontology_runtime_dump.stderr.txt", out + "\n")

    # 5) runtime state capture (no secrets)
    runtime_out = out_dir / "runtime_state.md"
    pip_freeze = ""
    rc2, pf = run([sys.executable, "-m", "pip", "freeze"], cwd=root)
    if rc2 == 0:
        pip_freeze = pf
    runtime = []
    runtime.append("# Runtime State\n\n")
    runtime.append(f"- generated_local: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    runtime.append(f"- git_branch: {git_branch}\n")
    runtime.append(f"- git_head: {git_head}\n")
    runtime.append(f"- python: {sys.version.split()[0]}\n")
    runtime.append(f"- python_executable: {sys.executable}\n")
    runtime.append(f"- base_url: {args.base}\n")
    runtime.append(f"- user: {args.user}\n")
    runtime.append("\n## Environment (presence only)\n\n")
    for k in [
        "WARDROBE_ENV", "WARDROBE_DEBUG", "WARDROBE_ALLOW_LOCAL_NOAUTH",
        "WARDROBE_MOUNT_FLASK", "WARDROBE_ONTOLOGY_MODE",
        "WARDROBE_API_KEY",
        "WARDROBE_ONTOLOGY_DIR",
        "WARDROBE_ONTOLOGY_OVERRIDES_FILE",
        "WARDROBE_ONTOLOGY_COLOR_LEXICON_FILE",
    ]:
        runtime.append(f"- {k}: {'SET' if os.getenv(k) else 'NOT_SET'}\n")
    runtime.append("\n## pip freeze\n\n```text\n")
    runtime.append(pip_freeze or "(pip freeze failed or empty)")
    runtime.append("\n```\n")
    write_text(runtime_out, "".join(runtime))
    steps.append(("runtime_state", 0, str(runtime_out)))

    # 6) copy templates (optional)
    for tpl in ["docs/HANDOFF_MANIFEST.md", "docs/HANDOFF_RUNTIME_STATE.md"]:
        src = root / tpl
        if src.exists():
            dst = out_dir / Path(tpl).name
            shutil.copyfile(src, dst)

    # 7) Summary / manifest instance
    summary_out = out_dir / "handoff_summary.md"
    summ = []
    summ.append("# Handoff Summary\n\n")
    summ.append(f"- timestamp: {stamp}\n")
    summ.append(f"- git_branch: {git_branch}\n")
    summ.append(f"- git_head: {git_head}\n")
    summ.append(f"- base_url: {args.base}\n")
    summ.append(f"- status: {'FAILED' if failed else 'OK'}\n\n")
    summ.append("## Steps\n\n| step | rc | output |\n|---|---:|---|\n")
    for name, rc, p in steps:
        summ.append(f"| `{name}` | {rc} | `{p}` |\n")
    summ.append("\n")
    write_text(summary_out, "".join(summ))

    # Update latest (copy, not symlink -> windows-safe)
    latest_dir = snap_root / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir, ignore_errors=True)
    shutil.copytree(out_dir, latest_dir)

    print(f"Handoff written to: {out_dir}")
    print(f"Latest updated: {latest_dir}")
    if failed:
        print("Handoff FAILED (see handoff_summary.md).")
        return 2
    print("Handoff OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
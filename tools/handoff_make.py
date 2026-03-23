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
import sys
from pathlib import Path

try:
    from tools.ops_common import copy_if_exists, now_stamp, run_command, write_text
except Exception:  # pragma: no cover - direct script execution fallback
    from ops_common import copy_if_exists, now_stamp, run_command, write_text  # type: ignore


def _runtime_state_markdown(*, git_branch: str, git_head: str, base_url: str, user: str, pip_freeze: str) -> str:
    lines: list[str] = []
    lines.append("# Runtime State\n\n")
    lines.append(f"- generated_local: {dt.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"- git_branch: {git_branch}\n")
    lines.append(f"- git_head: {git_head}\n")
    lines.append(f"- python: {sys.version.split()[0]}\n")
    lines.append(f"- python_executable: {sys.executable}\n")
    lines.append(f"- base_url: {base_url}\n")
    lines.append(f"- user: {user}\n")
    lines.append("\n## Environment (presence only)\n\n")
    for key in [
        "WARDROBE_ENV",
        "WARDROBE_DEBUG",
        "WARDROBE_ALLOW_LOCAL_NOAUTH",
        "WARDROBE_MOUNT_FLASK",
        "WARDROBE_ONTOLOGY_MODE",
        "WARDROBE_API_KEY",
        "WARDROBE_ONTOLOGY_DIR",
        "WARDROBE_ONTOLOGY_OVERRIDES_FILE",
        "WARDROBE_ONTOLOGY_COLOR_LEXICON_FILE",
    ]:
        lines.append(f"- {key}: {'SET' if os.getenv(key) else 'NOT_SET'}\n")
    lines.append("\n## pip freeze\n\n```text\n")
    lines.append(pip_freeze or "(pip freeze failed or empty)")
    lines.append("\n```\n")
    return "".join(lines)


def _handoff_summary_markdown(*, stamp: str, git_branch: str, git_head: str, base_url: str, steps: list[tuple[str, int, str]], failed: bool) -> str:
    lines: list[str] = []
    lines.append("# Handoff Summary\n\n")
    lines.append(f"- timestamp: {stamp}\n")
    lines.append(f"- git_branch: {git_branch}\n")
    lines.append(f"- git_head: {git_head}\n")
    lines.append(f"- base_url: {base_url}\n")
    lines.append(f"- status: {'FAILED' if failed else 'OK'}\n\n")
    lines.append("## Steps\n\n| step | rc | output |\n|---|---:|---|\n")
    for name, rc, output_path in steps:
        lines.append(f"| `{name}` | {rc} | `{output_path}` |\n")
    lines.append("\n")
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--base", default="http://127.0.0.1:5002", help="Server base url (server must be running)")
    ap.add_argument("--user", default="karen", help="User for sanity check urls")
    ap.add_argument("--ids", default="112,101,110", help="IDs for selection sanity check")
    ap.add_argument("--max-bytes", type=int, default=1_000_000, help="Max bytes per file in audit dump")
    ap.add_argument(
        "--include-ontology-text",
        action="store_true",
        help="Include ontology_part_*.md text inside ontology_runtime_dump.json (default: off)",
    )
    ap.add_argument(
        "--ontology-max-chars",
        type=int,
        default=250_000,
        help="Max chars per ontology MD part when included (default: 250000)",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    snap_root = root / "docs" / "_snapshot"
    stamp = now_stamp()
    out_dir = snap_root / f"handoff_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    steps: list[tuple[str, int, str]] = []
    failed = False

    rc, head = run_command(["git", "rev-parse", "HEAD"], cwd=root)
    git_head = head.splitlines()[-1].strip() if rc == 0 and head else "unknown"
    rc, branch = run_command(["git", "branch", "--show-current"], cwd=root)
    git_branch = branch.strip() if rc == 0 and branch else "unknown"

    sanity_out = out_dir / "sanity_check.txt"
    rc, out = run_command(
        [sys.executable, "tools/project_sanity_check.py", "--base", args.base, "--user", args.user, "--ids", args.ids],
        cwd=root,
    )
    write_text(sanity_out, out + "\n")
    steps.append(("sanity_check", rc, str(sanity_out)))
    if rc != 0:
        failed = True

    audit_out = out_dir / "project_audit_dump.md"
    rc, out = run_command(
        [
            sys.executable,
            "tools/project_audit_dump.py",
            "--root",
            ".",
            "--out",
            str(audit_out),
            "--max-bytes",
            str(args.max_bytes),
        ],
        cwd=root,
    )
    steps.append(("project_audit_dump", rc, str(audit_out)))
    if rc != 0:
        failed = True
        write_text(out_dir / "project_audit_dump.stderr.txt", out + "\n")

    data_out = out_dir / "data_snapshot.md"
    rc, out = run_command(
        [sys.executable, "tools/project_data_snapshot.py", "--root", ".", "--out", str(data_out)],
        cwd=root,
    )
    steps.append(("project_data_snapshot", rc, str(data_out)))
    if rc != 0:
        failed = True
        write_text(out_dir / "data_snapshot.stderr.txt", out + "\n")

    onto_json = out_dir / "ontology_runtime_dump.json"
    onto_md = out_dir / "ontology_runtime_summary.md"
    cmd = [
        sys.executable,
        "tools/ontology_runtime_dump.py",
        "--root",
        ".",
        "--out-json",
        str(onto_json),
        "--out-md",
        str(onto_md),
        "--max-part-chars",
        str(args.ontology_max_chars),
    ]
    if args.include_ontology_text:
        cmd.append("--include-part-text")

    rc, out = run_command(cmd, cwd=root)
    steps.append(("ontology_runtime_dump", rc, f"{onto_json} / {onto_md}"))
    if rc != 0:
        failed = True
        write_text(out_dir / "ontology_runtime_dump.stderr.txt", out + "\n")

    runtime_out = out_dir / "runtime_state.md"
    rc, pip_freeze = run_command([sys.executable, "-m", "pip", "freeze"], cwd=root)
    if rc != 0:
        pip_freeze = ""
    write_text(
        runtime_out,
        _runtime_state_markdown(
            git_branch=git_branch,
            git_head=git_head,
            base_url=args.base,
            user=args.user,
            pip_freeze=pip_freeze,
        ),
    )
    steps.append(("runtime_state", 0, str(runtime_out)))

    for template in ["docs/HANDOFF_MANIFEST.md", "docs/HANDOFF_RUNTIME_STATE.md"]:
        copy_if_exists(root / template, out_dir / Path(template).name)

    summary_out = out_dir / "handoff_summary.md"
    write_text(
        summary_out,
        _handoff_summary_markdown(
            stamp=stamp,
            git_branch=git_branch,
            git_head=git_head,
            base_url=args.base,
            steps=steps,
            failed=failed,
        ),
    )

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

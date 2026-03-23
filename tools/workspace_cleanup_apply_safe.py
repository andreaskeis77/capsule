from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
OPS_DIR = REPO_ROOT / "docs" / "_ops" / "workspace_cleanup"
ARCHIVE_ROOT = REPO_ROOT / "docs" / "_archive" / "workspace_cleanup"

PROTECTED_ROOT_FILES = {"capsule.ps1", "requirements-dev.txt"}

ROOT_ARCHIVE_CANDIDATES = [
    "APPLY_TRANCHE_A.md",
    "APPLY_TRANCHE_A_FIX_1.md",
    "APPLY_TRANCHE_B.md",
    "APPLY_TRANCHE_C.md",
    "APPLY_TRANCHE_D.md",
    "APPLY_TRANCHE_E.md",
    "APPLY_TRANCHE_F.md",
    "APPLY_TRANCHE_G.md",
    "APPLY_TRANCHE_H.md",
    "APPLY_TRANCHE_I.md",
    "APPLY_TRANCHE_J.md",
    "APPLY_TRANCHE_K.md",
    "APPLY_TRANCHE_L.md",
    "APPLY_TRANCHE_M.md",
    "APPLY_TRANCHE_N.md",
    "APPLY_TRANCHE_O.md",
    "APPLY_TRANCHE_P.md",
    "APPLY_TRANCHE_Q.md",
    "APPLY_TRANCHE_R.md",
    "APPLY_WORKSPACE_INVENTORY.md",
    "README_CapsuleKnowledgeRefresh.md",
    "Run-CapsuleKnowledgeRefresh.ps1",
    "Test-CapsuleKnowledgeRefresh.ps1",
]

DELETE_CANDIDATES = [
    ".env.bak",
    "capsule_server_seed.zip",
    "logs/server_startup.log",
    "logs/wardrobe.log",
]

ARCHIVE_DIR_CANDIDATES = [("docs/_metrics", "docs_metrics")]


@dataclass
class PlannedAction:
    relative_path: str
    action: str
    target: str
    reason: str
    status: str = "planned"
    bytes: int = 0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def to_posix(rel_path: Path | str) -> str:
    return Path(rel_path).as_posix()


def safe_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def archive_target(stamp: str, rel_path: str) -> Path:
    rel = Path(rel_path)
    if len(rel.parts) == 1:
        return ARCHIVE_ROOT / stamp / "root_notes" / rel.name
    return ARCHIVE_ROOT / stamp / rel


def build_plan(stamp: str) -> List[PlannedAction]:
    plan: List[PlannedAction] = []

    for rel in ROOT_ARCHIVE_CANDIDATES:
        if Path(rel).name in PROTECTED_ROOT_FILES:
            continue
        src = REPO_ROOT / rel
        if src.exists():
            target = archive_target(stamp, rel).relative_to(REPO_ROOT)
            plan.append(
                PlannedAction(
                    relative_path=rel,
                    action="archive_move",
                    target=to_posix(target),
                    reason="root work note/script",
                    bytes=safe_size(src),
                )
            )

    for rel, target_name in ARCHIVE_DIR_CANDIDATES:
        src = REPO_ROOT / rel
        if src.exists():
            target = (ARCHIVE_ROOT / stamp / target_name).relative_to(REPO_ROOT)
            plan.append(
                PlannedAction(
                    relative_path=rel,
                    action="archive_move",
                    target=to_posix(target),
                    reason="generated metrics output",
                    bytes=safe_size(src),
                )
            )

    reason_map = {
        ".env.bak": "backup env file",
        "capsule_server_seed.zip": "large root export zip",
        "logs/server_startup.log": "replaceable runtime log",
        "logs/wardrobe.log": "replaceable runtime log",
    }
    for rel in DELETE_CANDIDATES:
        if Path(rel).name in PROTECTED_ROOT_FILES:
            continue
        src = REPO_ROOT / rel
        if src.exists():
            plan.append(
                PlannedAction(
                    relative_path=rel,
                    action="delete",
                    target="",
                    reason=reason_map.get(rel, "cleanup candidate"),
                    bytes=safe_size(src),
                )
            )

    plan.sort(key=lambda x: x.relative_path.lower())
    return plan


def execute_plan(plan: List[PlannedAction], apply: bool) -> None:
    for item in plan:
        src = REPO_ROOT / item.relative_path
        try:
            if item.action == "archive_move":
                target = REPO_ROOT / item.target
                if apply:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(target))
                    item.status = "applied"
            elif item.action == "delete":
                if apply:
                    if src.is_dir():
                        shutil.rmtree(src)
                    elif src.exists():
                        src.unlink()
                    item.status = "applied"
        except Exception as exc:
            item.status = f"error: {exc}"


def write_artifacts(plan: List[PlannedAction], stamp: str, apply: bool) -> Path:
    run_dir = OPS_DIR / f"run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    planned_bytes = sum(p.bytes for p in plan)
    archive_moves = sum(1 for p in plan if p.action == "archive_move")
    deletes = sum(1 for p in plan if p.action == "delete")
    statuses = {}
    for p in plan:
        statuses[p.status] = statuses.get(p.status, 0) + 1

    lines = [
        "# Workspace Cleanup Plan",
        "",
        f"- generated_utc: {utc_now()}",
        f"- repo_root: `{REPO_ROOT}`",
        f"- mode: `{'apply' if apply else 'dry-run'}`",
        "",
        "## Plan Summary",
        "",
        f"- planned_items: {len(plan)}",
        f"- planned_bytes: {planned_bytes} ({planned_bytes / (1024*1024):.2f} MB)",
        f"- planned_archive_moves: {archive_moves}",
        f"- planned_deletes: {deletes}",
        "",
        "## Protected Files Kept In Place",
        "",
    ]
    for name in sorted(PROTECTED_ROOT_FILES):
        lines.append(f"- `{name}`")
    lines += ["", "## Execution Status", "", "| status | count |", "| --- | ---: |"]
    for status, count in sorted(statuses.items()):
        lines.append(f"| {status} | {count} |")
    lines += ["", "## Selected Actions", "", "| relative_path | action | target | reason |", "| --- | --- | --- | --- |"]
    for p in plan:
        lines.append(f"| `{p.relative_path}` | {p.action} | `{p.target}` | {p.reason} |")

    (run_dir / "cleanup_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (run_dir / "cleanup_manifest.json").write_text(
        json.dumps(
            {
                "generated_utc": utc_now(),
                "repo_root": str(REPO_ROOT),
                "mode": "apply" if apply else "dry-run",
                "protected_root_files": sorted(PROTECTED_ROOT_FILES),
                "plan": [asdict(p) for p in plan],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with (run_dir / "cleanup_actions.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "action", "target", "reason", "status", "bytes"])
        writer.writeheader()
        for p in plan:
            writer.writerow(asdict(p))

    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservative workspace cleanup for Capsule repo.")
    parser.add_argument("--apply", action="store_true", help="Execute the plan. Default is dry-run.")
    args = parser.parse_args()

    stamp = run_stamp()
    plan = build_plan(stamp)
    execute_plan(plan, apply=args.apply)
    run_dir = write_artifacts(plan, stamp, apply=args.apply)

    print(f"[OK] workspace cleanup {'applied' if args.apply else 'planned'}: {run_dir}")
    print("[ARTIFACTS]")
    print("- cleanup_summary.md")
    print("- cleanup_actions.csv")
    print("- cleanup_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

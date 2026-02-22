#!/usr/bin/env python3
from __future__ import annotations

# ---- bootstrap: ensure repo root importable (so `import src` works from anywhere) ----
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
# ------------------------------------------------------------------------------------

import argparse
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from src import settings
from src.db_schema import ensure_schema
from src.run_registry import start_run


VALID_USERS = {"andreas", "karen"}


def _folder_signature_fingerprint(item_dir: Path) -> str:
    import hashlib

    entries: List[Dict[str, Any]] = []
    for p in sorted(item_dir.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(item_dir).as_posix()
        except Exception:
            rel = p.name
        try:
            size = p.stat().st_size
        except Exception:
            size = None
        entries.append({"rel": rel, "size": size})

    blob = json.dumps(entries, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Recover orphaned archive folders into DB (run-registry instrumented).")
    ap.add_argument("--archive-dir", type=str, default=str(settings.IMG_DIR))
    ap.add_argument("--user", type=str, default="", help="andreas|karen or empty for all")
    ap.add_argument("--dry-run", action="store_true", help="Report only, do not write DB")
    ap.add_argument("--limit", type=int, default=0, help="Stop after N recoveries (0 unlimited)")
    ap.add_argument("--promote-pending", action="store_true", help="If DB row pending/failed but folder exists, set ok")
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    settings.reload_settings()
    ensure_schema()
    args = parse_args(argv)

    archive_dir = Path(args.archive_dir)
    if not archive_dir.exists():
        raise SystemExit(f"Missing archive dir: {archive_dir}")

    user_filter = args.user.strip().lower()
    if user_filter and user_filter not in VALID_USERS:
        raise SystemExit(f"Invalid user: {user_filter}")

    meta = {
        "archive_dir": str(archive_dir),
        "user": user_filter or None,
        "dry_run": bool(args.dry_run),
        "limit": args.limit,
        "promote_pending": bool(args.promote_pending),
    }

    run = start_run("tools", "ingest_recover", meta=meta)
    run.event("recover.start", data=meta)

    recoveries = 0
    promotions = 0
    skipped = 0

    conn = _connect()
    try:
        cur = conn.cursor()

        users = [user_filter] if user_filter else [p.name for p in archive_dir.iterdir() if p.is_dir()]
        for user in sorted(users):
            if user not in VALID_USERS:
                continue
            udir = archive_dir / user
            if not udir.is_dir():
                continue

            for item_dir in sorted([p for p in udir.iterdir() if p.is_dir()]):
                image_path = f"{user}/{item_dir.name}"
                fp = _folder_signature_fingerprint(item_dir)

                # find DB row by fingerprint (preferred)
                cur.execute(
                    "SELECT id, ingest_status, image_path FROM items WHERE user_id=? AND source_fingerprint=? LIMIT 1",
                    (user, fp),
                )
                row = cur.fetchone()

                if row is None:
                    # fallback by image_path
                    cur.execute(
                        "SELECT id, ingest_status, source_fingerprint FROM items WHERE user_id=? AND image_path=? LIMIT 1",
                        (user, image_path),
                    )
                    row2 = cur.fetchone()
                    if row2 is None:
                        # orphan folder => recover
                        if args.dry_run:
                            recoveries += 1
                            run.event("recover.orphan_folder", data={"user": user, "image_path": image_path, "fp": fp})
                        else:
                            cur.execute(
                                """
                                INSERT INTO items (user_id, name, image_path, source_fingerprint, ingest_status, ingest_error)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (user, item_dir.name, image_path, fp, "ok", "RecoveredFromArchive"),
                            )
                            conn.commit()
                            recoveries += 1
                            run.event("recover.inserted", data={"user": user, "image_path": image_path, "fp": fp})
                    else:
                        # row exists by image_path but missing fingerprint -> attach it
                        if args.dry_run:
                            skipped += 1
                            run.event("recover.attach_fp_dry", data={"user": user, "image_path": image_path, "fp": fp, "item_id": int(row2["id"])})
                        else:
                            cur.execute(
                                "UPDATE items SET source_fingerprint=? WHERE id=?",
                                (fp, int(row2["id"])),
                            )
                            conn.commit()
                            run.event("recover.attached_fp", data={"user": user, "image_path": image_path, "fp": fp, "item_id": int(row2["id"])})
                            skipped += 1
                else:
                    # row exists by fingerprint
                    st = (row["ingest_status"] or "").lower()
                    if args.promote_pending and st in {"pending", "failed"}:
                        if args.dry_run:
                            promotions += 1
                            run.event("recover.promote_dry", data={"user": user, "item_id": int(row["id"]), "from": st, "to": "ok"})
                        else:
                            cur.execute(
                                "UPDATE items SET ingest_status='ok', ingest_error='RecoveredPromote' WHERE id=?",
                                (int(row["id"]),),
                            )
                            conn.commit()
                            promotions += 1
                            run.event("recover.promoted", data={"user": user, "item_id": int(row["id"]), "from": st, "to": "ok"})
                    else:
                        skipped += 1

                if args.limit and (recoveries + promotions) >= args.limit:
                    break
            if args.limit and (recoveries + promotions) >= args.limit:
                break

    finally:
        conn.close()

    summary = f"recoveries={recoveries} promotions={promotions} skipped={skipped} dry_run={args.dry_run}"
    run.event("recover.done", data={"recoveries": recoveries, "promotions": promotions, "skipped": skipped})
    run.ok(summary=summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
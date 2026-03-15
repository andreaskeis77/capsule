# FILE: src/ingest_wardrobe.py
from __future__ import annotations

# ---- bootstrap: ensure repo root importable (so `import src` works even when run as script) ----
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
# ---------------------------------------------------------------------------------------------

import argparse
import gc
import logging
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass
from typing import List, Optional

from src import settings
from src.db_schema import ensure_schema
from src.ingest_item_ai import (
    analyze_item_hybrid,
    fake_ai as _fake_ai,
    get_openai_client as _get_openai_client,
)
from src.ingest_item_db import (
    claim_pending as _db_claim_pending,
    connect_db,
    get_by_fingerprint as _db_get_by_fingerprint,
    mark_failed as _db_mark_failed,
    mark_ok as _db_mark_ok,
    run_with_connection,
)
from src.ingest_item_io import (
    VALID_IMAGE_EXTS,
    VALID_TEXT_EXTS,
    encode_bytes as _encode_bytes,
    folder_signature_fingerprint as _folder_signature_fingerprint,
    image_to_data_url as _image_to_data_url,
    list_image_files as _list_image_files,
    read_text_files as _read_text_files,
)
from src.run_registry import start_run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("WardrobeIngest")

VALID_USERS = {"andreas", "karen"}
@dataclass
class Stats:
    scanned: int = 0
    processed: int = 0
    ok: int = 0
    failed: int = 0
    skipped: int = 0
    quarantined: int = 0


def _now_s() -> float:
    return time.perf_counter()


def _connect_ro() -> sqlite3.Connection:
    return connect_db(settings.DB_PATH)


def _with_write_connection(operation, *args, **kwargs):
    return run_with_connection(settings.DB_PATH, operation, *args, **kwargs)


def _robust_rmtree(path: Path) -> None:
    import stat
    import inspect

    has_onexc = "onexc" in inspect.signature(shutil.rmtree).parameters

    def _make_writable(p) -> None:
        try:
            os.chmod(p, stat.S_IWRITE)
        except Exception:
            pass

    def _onerror(func, p, exc_info):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    def _onexc(func, p, exc):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    if not path.exists():
        return

    if has_onexc:
        shutil.rmtree(path, onexc=_onexc)
    else:
        shutil.rmtree(path, onerror=_onerror)


def robust_move(src: Path, dst: Path, *, retries: int = 3, delay_s: float = 0.8) -> bool:
    for i in range(retries):
        try:
            if dst.exists():
                _robust_rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return True
        except PermissionError:
            logger.warning("PermissionError, retrying (%d/%d)...", i + 1, retries)
            time.sleep(delay_s)
        except Exception as e:
            logger.error("Move failed: %s", e)
            break
    return False


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Wardrobe Studio ingestion (idempotent + run-registry).")

    ap.add_argument(
        "--input-dir",
        type=str,
        default=str(settings.BASE_DIR / "01_raw_input"),
        help="Root of raw input (default: 01_raw_input)",
    )
    ap.add_argument(
        "--archive-dir",
        type=str,
        default=str(settings.IMG_DIR),
        help="Archive/images dir (default: settings.IMG_DIR / 02_wardrobe_images)",
    )
    ap.add_argument(
        "--quarantine-dir",
        type=str,
        default=str(settings.BASE_DIR / "04_user_data" / "quarantine_input"),
        help="Where duplicates/conflicts are moved (default: 04_user_data/quarantine_input)",
    )

    ap.add_argument("--user", type=str, default="", help="Only ingest for this user (andreas|karen). Empty = all.")
    ap.add_argument("--max-items", type=int, default=0, help="Stop after N processed items (0 = unlimited).")
    ap.add_argument("--dry-run", action="store_true", help="No OpenAI, no DB writes, no moves.")
    ap.add_argument("--fake-ai", action="store_true", help="No OpenAI. Still moves + writes DB (test/CI friendly).")

    ap.add_argument("--model", type=str, default=os.environ.get("WARDROBE_INGEST_MODEL", "gpt-4o-mini"))
    ap.add_argument("--max-images", type=int, default=3, help="Max images sent to OpenAI per item (default 3).")
    ap.add_argument("--force", action="store_true", help="Process even if fingerprint already ingested / conflicts.")
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    settings.reload_settings()
    ensure_schema()

    args = parse_args(argv)
    input_dir = Path(args.input_dir)
    archive_dir = Path(args.archive_dir)
    quarantine_dir = Path(args.quarantine_dir)

    meta = {
        "input_dir": str(input_dir),
        "archive_dir": str(archive_dir),
        "quarantine_dir": str(quarantine_dir),
        "user": args.user or None,
        "max_items": args.max_items,
        "dry_run": bool(args.dry_run),
        "fake_ai": bool(args.fake_ai),
        "model": args.model,
        "max_images": args.max_images,
        "force": bool(args.force),
    }

    run = start_run("ingest", "wardrobe_ingest", meta=meta)
    t0 = _now_s()

    try:
        run.event("ingest.start", data=meta)

        if not input_dir.exists():
            run.event("ingest.input_missing", level="ERROR", message=f"Missing input dir: {input_dir}")
            run.fail(summary=f"MissingInputDir: {input_dir}")
            return 2

        # determine users
        if args.user:
            u = args.user.strip().lower()
            if u not in VALID_USERS:
                run.event("ingest.invalid_user", level="ERROR", message=f"Invalid user: {u}")
                run.fail(summary=f"InvalidUser: {u}")
                return 2
            users = [u]
        else:
            users = [p.name for p in sorted(input_dir.iterdir()) if p.is_dir()]

        stats = Stats()

        conn = _connect_ro()
        try:
            for user in users:
                user = user.strip().lower()
                if user not in VALID_USERS:
                    run.event("ingest.skip_unknown_user_dir", level="WARN", message=f"Skipping dir: {user}")
                    continue

                u_path = input_dir / user
                if not u_path.exists():
                    run.event("ingest.user_dir_missing", level="WARN", message=f"Missing: {u_path}")
                    continue

                item_dirs = [p for p in sorted(u_path.iterdir()) if p.is_dir()]
                run.event("ingest.user.scan", data={"user": user, "items": len(item_dirs)})

                for item_dir in item_dirs:
                    if args.max_items and stats.processed >= args.max_items:
                        run.event("ingest.max_items_reached", data={"max_items": args.max_items})
                        break

                    stats.scanned += 1
                    item_name = item_dir.name

                    # gather content
                    img_files = _list_image_files(item_dir)
                    txt_context = _read_text_files(item_dir)

                    if not img_files and not txt_context:
                        stats.skipped += 1
                        run.event("item.skip_empty", level="WARN", data={"user": user, "item": item_name})
                        continue

                    fp = _folder_signature_fingerprint(item_dir)
                    dest_rel = f"{user}/{item_name}"
                    dest_dir = archive_dir / user / item_name

                    run.event("item.start", data={"user": user, "item": item_name, "fingerprint": fp[:12]})

                    # Fast skip: fingerprint already ingested OK
                    existing = _db_get_by_fingerprint(conn, user, fp)
                    if existing and (existing["ingest_status"] or "").lower() == "ok" and (not args.force):
                        # move duplicate out of input to quarantine
                        quarantine_target = quarantine_dir / user / f"{item_name}__dup__{fp[:8]}"
                        ok_q = robust_move(item_dir, quarantine_target)
                        stats.skipped += 1
                        stats.quarantined += 1 if ok_q else 0
                        run.event(
                            "item.dup.skip",
                            level="WARN",
                            data={
                                "user": user,
                                "item": item_name,
                                "fingerprint": fp,
                                "quarantine_ok": ok_q,
                                "quarantine_target": str(quarantine_target),
                                "existing_item_id": int(existing["id"]),
                            },
                        )
                        continue

                    # dry-run: simulate only (no DB, no moves, no OpenAI)
                    if args.dry_run:
                        stats.processed += 1
                        stats.ok += 1
                        run.event(
                            "item.dry_run",
                            data={
                                "user": user,
                                "item": item_name,
                                "fingerprint": fp,
                                "images": len(img_files),
                                "text_chars": len(txt_context),
                                "would_move_to": str(dest_dir),
                                "would_insert_image_path": dest_rel,
                            },
                        )
                        continue

                    # claim pending row (prevents orphan moves)
                    stats.processed += 1
                    try:
                        item_id = _with_write_connection(
                            _db_claim_pending,
                            user=user,
                            item_name=item_name,
                            image_path=dest_rel,
                            fp=fp,
                            run_id=run.run_id,
                        )
                    except Exception as e:
                        stats.failed += 1
                        run.event("item.claim_failed", level="ERROR", message=str(e), data={"user": user, "item": item_name})
                        continue

                    # analyze (fake-ai or OpenAI)
                    if args.fake_ai:
                        data = _fake_ai(item_name, txt_context)
                    else:
                        run.event("item.analyze.start", data={"user": user, "item": item_name, "images": len(img_files), "text_chars": len(txt_context)})
                        data = analyze_item_hybrid(img_files, txt_context, model=args.model, max_images=args.max_images)

                    if not data:
                        stats.failed += 1
                        try:
                            _with_write_connection(_db_mark_failed, item_id=item_id, err="AnalyzeFailed", run_id=run.run_id)
                        except Exception:
                            pass
                        run.event("item.analyze.failed", level="ERROR", data={"user": user, "item": item_name, "item_id": item_id})
                        continue

                    # close file handles before move (Windows)
                    gc.collect()

                    moved_this_run = False

                    # move folder into archive if needed
                    if dest_dir.exists():
                        if item_dir.exists():
                            if args.force:
                                moved_this_run = robust_move(item_dir, dest_dir)
                                if not moved_this_run:
                                    stats.failed += 1
                                    run.event("item.move.failed", level="ERROR", data={"user": user, "item": item_name, "dest_dir": str(dest_dir), "item_id": item_id})
                                    continue
                            else:
                                # conflict: both src and dest exist -> quarantine src
                                quarantine_target = quarantine_dir / user / f"{item_name}__conflict__{fp[:8]}"
                                ok_q = robust_move(item_dir, quarantine_target)
                                stats.failed += 1
                                stats.quarantined += 1 if ok_q else 0
                                try:
                                    _with_write_connection(
                                        _db_mark_failed,
                                        item_id=item_id,
                                        err="ConflictSrcAndDestExist",
                                        run_id=run.run_id,
                                    )
                                except Exception:
                                    pass
                                run.event(
                                    "item.conflict.src_and_dest_exist",
                                    level="ERROR",
                                    data={
                                        "user": user,
                                        "item": item_name,
                                        "item_id": item_id,
                                        "dest_dir": str(dest_dir),
                                        "quarantine_ok": ok_q,
                                        "quarantine_target": str(quarantine_target),
                                    },
                                )
                                continue
                        else:
                            # src already gone; dest exists -> recovery path
                            run.event("item.recover.dest_exists", data={"user": user, "item": item_name, "item_id": item_id, "dest_dir": str(dest_dir)})
                    else:
                        if not item_dir.exists():
                            stats.failed += 1
                            try:
                                _with_write_connection(_db_mark_failed, item_id=item_id, err="SourceMissing", run_id=run.run_id)
                            except Exception:
                                pass
                            run.event("item.source_missing", level="ERROR", data={"user": user, "item": item_name, "item_id": item_id})
                            continue
                        moved_this_run = robust_move(item_dir, dest_dir)
                        if not moved_this_run:
                            stats.failed += 1
                            try:
                                _with_write_connection(_db_mark_failed, item_id=item_id, err="MoveFailed", run_id=run.run_id)
                            except Exception:
                                pass
                            run.event("item.move.failed", level="ERROR", data={"user": user, "item": item_name, "dest_dir": str(dest_dir), "item_id": item_id})
                            continue

                    # DB update OK
                    try:
                        _with_write_connection(_db_mark_ok, item_id=item_id, data=data, run_id=run.run_id)

                        stats.ok += 1
                        run.event("item.ok", data={"user": user, "item": item_name, "item_id": item_id, "image_path": dest_rel})

                    except Exception as e:
                        stats.failed += 1
                        run.event("item.db_update_failed", level="ERROR", message=str(e), data={"user": user, "item": item_name, "item_id": item_id})

                        # rollback move if we moved this run
                        if moved_this_run and dest_dir.exists():
                            rollback_target = input_dir / user / item_name
                            ok_rb = robust_move(dest_dir, rollback_target)
                            run.event("item.rollback_move", data={"ok": ok_rb, "user": user, "item": item_name, "item_id": item_id})
                        try:
                            _with_write_connection(
                                _db_mark_failed,
                                item_id=item_id,
                                err=f"DbUpdateFailed:{type(e).__name__}",
                                run_id=run.run_id,
                            )
                        except Exception:
                            pass

            # end loops
        finally:
            conn.close()

        dur_ms = int((_now_s() - t0) * 1000)
        summary = (
            f"scanned={stats.scanned} processed={stats.processed} ok={stats.ok} failed={stats.failed} "
            f"skipped={stats.skipped} quarantined={stats.quarantined} dry_run={args.dry_run} fake_ai={args.fake_ai} dur_ms={dur_ms}"
        )
        run.event("ingest.done", data={"stats": stats.__dict__, "dur_ms": dur_ms})

        if stats.failed > 0 and stats.ok > 0:
            run.partial(summary=summary)
            return 2
        if stats.failed > 0 and stats.ok == 0:
            run.fail(summary=summary)
            return 2

        run.ok(summary=summary)
        return 0

    except Exception as e:
        run.event("ingest.exception", level="ERROR", message=str(e))
        run.fail(summary=f"{type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
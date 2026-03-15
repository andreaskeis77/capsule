from __future__ import annotations

import gc
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set


@dataclass
class Stats:
    scanned: int = 0
    processed: int = 0
    ok: int = 0
    failed: int = 0
    skipped: int = 0
    quarantined: int = 0


def build_run_meta(
    args: Any,
    *,
    input_dir: Path,
    archive_dir: Path,
    quarantine_dir: Path,
) -> Dict[str, Any]:
    return {
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


def summarize_stats(stats: Stats, *, dry_run: bool, fake_ai: bool, dur_ms: int) -> str:
    return (
        f"scanned={stats.scanned} processed={stats.processed} ok={stats.ok} failed={stats.failed} "
        f"skipped={stats.skipped} quarantined={stats.quarantined} dry_run={dry_run} fake_ai={fake_ai} dur_ms={dur_ms}"
    )


def resolve_requested_users(*, args_user: str, input_dir: Path, valid_users: Set[str], run: Any) -> tuple[Optional[List[str]], Optional[int]]:
    if args_user:
        user = args_user.strip().lower()
        if user not in valid_users:
            run.event("ingest.invalid_user", level="ERROR", message=f"Invalid user: {user}")
            run.fail(summary=f"InvalidUser: {user}")
            return None, 2
        return [user], None

    users = [p.name for p in sorted(input_dir.iterdir()) if p.is_dir()]
    return users, None


def run_ingest(
    *,
    args: Any,
    run: Any,
    t0: float,
    now_s: Callable[[], float],
    input_dir: Path,
    archive_dir: Path,
    quarantine_dir: Path,
    valid_users: Set[str],
    connect_ro: Callable[[], Any],
    write_connection: Callable[..., Any],
    list_image_files: Callable[[Path], Sequence[Path]],
    read_text_files: Callable[[Path], str],
    folder_signature_fingerprint: Callable[[Path], str],
    db_get_by_fingerprint: Callable[[Any, str, str], Any],
    db_claim_pending: Callable[..., int],
    db_mark_ok: Callable[..., None],
    db_mark_failed: Callable[..., None],
    robust_move: Callable[[Path, Path], bool],
    analyze_item_hybrid: Callable[..., Optional[Dict[str, Any]]],
    fake_ai: Callable[[str, str], Dict[str, Any]],
) -> int:
    meta = build_run_meta(args, input_dir=input_dir, archive_dir=archive_dir, quarantine_dir=quarantine_dir)

    try:
        run.event("ingest.start", data=meta)

        if not input_dir.exists():
            run.event("ingest.input_missing", level="ERROR", message=f"Missing input dir: {input_dir}")
            run.fail(summary=f"MissingInputDir: {input_dir}")
            return 2

        users, exit_code = resolve_requested_users(
            args_user=args.user,
            input_dir=input_dir,
            valid_users=valid_users,
            run=run,
        )
        if exit_code is not None:
            return exit_code
        assert users is not None

        stats = Stats()

        conn = connect_ro()
        try:
            for user in users:
                user = user.strip().lower()
                if user not in valid_users:
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

                    img_files = list_image_files(item_dir)
                    txt_context = read_text_files(item_dir)

                    if not img_files and not txt_context:
                        stats.skipped += 1
                        run.event("item.skip_empty", level="WARN", data={"user": user, "item": item_name})
                        continue

                    fp = folder_signature_fingerprint(item_dir)
                    dest_rel = f"{user}/{item_name}"
                    dest_dir = archive_dir / user / item_name

                    run.event("item.start", data={"user": user, "item": item_name, "fingerprint": fp[:12]})

                    existing = db_get_by_fingerprint(conn, user, fp)
                    if existing and (existing["ingest_status"] or "").lower() == "ok" and (not args.force):
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

                    stats.processed += 1
                    try:
                        item_id = write_connection(
                            db_claim_pending,
                            user=user,
                            item_name=item_name,
                            image_path=dest_rel,
                            fp=fp,
                            run_id=run.run_id,
                        )
                    except Exception as exc:
                        stats.failed += 1
                        run.event("item.claim_failed", level="ERROR", message=str(exc), data={"user": user, "item": item_name})
                        continue

                    if args.fake_ai:
                        data = fake_ai(item_name, txt_context)
                    else:
                        run.event(
                            "item.analyze.start",
                            data={"user": user, "item": item_name, "images": len(img_files), "text_chars": len(txt_context)},
                        )
                        data = analyze_item_hybrid(img_files, txt_context, model=args.model, max_images=args.max_images)

                    if not data:
                        stats.failed += 1
                        try:
                            write_connection(db_mark_failed, item_id=item_id, err="AnalyzeFailed", run_id=run.run_id)
                        except Exception:
                            pass
                        run.event("item.analyze.failed", level="ERROR", data={"user": user, "item": item_name, "item_id": item_id})
                        continue

                    gc.collect()
                    moved_this_run = False

                    if dest_dir.exists():
                        if item_dir.exists():
                            if args.force:
                                moved_this_run = robust_move(item_dir, dest_dir)
                                if not moved_this_run:
                                    stats.failed += 1
                                    run.event(
                                        "item.move.failed",
                                        level="ERROR",
                                        data={"user": user, "item": item_name, "dest_dir": str(dest_dir), "item_id": item_id},
                                    )
                                    continue
                            else:
                                quarantine_target = quarantine_dir / user / f"{item_name}__conflict__{fp[:8]}"
                                ok_q = robust_move(item_dir, quarantine_target)
                                stats.failed += 1
                                stats.quarantined += 1 if ok_q else 0
                                try:
                                    write_connection(
                                        db_mark_failed,
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
                            run.event(
                                "item.recover.dest_exists",
                                data={"user": user, "item": item_name, "item_id": item_id, "dest_dir": str(dest_dir)},
                            )
                    else:
                        if not item_dir.exists():
                            stats.failed += 1
                            try:
                                write_connection(db_mark_failed, item_id=item_id, err="SourceMissing", run_id=run.run_id)
                            except Exception:
                                pass
                            run.event("item.source_missing", level="ERROR", data={"user": user, "item": item_name, "item_id": item_id})
                            continue
                        moved_this_run = robust_move(item_dir, dest_dir)
                        if not moved_this_run:
                            stats.failed += 1
                            try:
                                write_connection(db_mark_failed, item_id=item_id, err="MoveFailed", run_id=run.run_id)
                            except Exception:
                                pass
                            run.event(
                                "item.move.failed",
                                level="ERROR",
                                data={"user": user, "item": item_name, "dest_dir": str(dest_dir), "item_id": item_id},
                            )
                            continue

                    try:
                        write_connection(db_mark_ok, item_id=item_id, data=data, run_id=run.run_id)
                        stats.ok += 1
                        run.event("item.ok", data={"user": user, "item": item_name, "item_id": item_id, "image_path": dest_rel})
                    except Exception as exc:
                        stats.failed += 1
                        run.event(
                            "item.db_update_failed",
                            level="ERROR",
                            message=str(exc),
                            data={"user": user, "item": item_name, "item_id": item_id},
                        )
                        if moved_this_run and dest_dir.exists():
                            rollback_target = input_dir / user / item_name
                            ok_rb = robust_move(dest_dir, rollback_target)
                            run.event("item.rollback_move", data={"ok": ok_rb, "user": user, "item": item_name, "item_id": item_id})
                        try:
                            write_connection(
                                db_mark_failed,
                                item_id=item_id,
                                err=f"DbUpdateFailed:{type(exc).__name__}",
                                run_id=run.run_id,
                            )
                        except Exception:
                            pass
        finally:
            conn.close()

        dur_ms = int((now_s() - t0) * 1000)
        summary = summarize_stats(stats, dry_run=bool(args.dry_run), fake_ai=bool(args.fake_ai), dur_ms=dur_ms)
        run.event("ingest.done", data={"stats": stats.__dict__, "dur_ms": dur_ms})

        if stats.failed > 0 and stats.ok > 0:
            run.partial(summary=summary)
            return 2
        if stats.failed > 0 and stats.ok == 0:
            run.fail(summary=summary)
            return 2

        run.ok(summary=summary)
        return 0

    except Exception as exc:
        run.event("ingest.exception", level="ERROR", message=str(exc))
        run.fail(summary=f"{type(exc).__name__}: {exc}")
        raise

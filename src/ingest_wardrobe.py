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
import base64
import gc
import json
import logging
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src import settings
from src.db_schema import ensure_schema
from src.run_registry import start_run

# --- Logging (CLI-friendly) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("WardrobeIngest")

VALID_USERS = {"andreas", "karen"}
VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".jfif", ".heic"}  # heic best-effort
VALID_TEXT_EXTS = {".txt"}


@dataclass
class Stats:
    scanned: int = 0
    processed: int = 0
    ok: int = 0
    failed: int = 0
    skipped: int = 0


def _now_s() -> float:
    return time.perf_counter()


def _read_text_files(item_dir: Path) -> str:
    parts: List[str] = []
    for p in sorted(item_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in VALID_TEXT_EXTS:
            try:
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                logger.exception("Failed reading text file: %s", p)
    return "\n".join(parts).strip()


def _list_image_files(item_dir: Path) -> List[Path]:
    imgs: List[Path] = []
    for p in sorted(item_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in VALID_IMAGE_EXTS:
            imgs.append(p)
    return imgs


def _encode_bytes(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _image_to_data_url(path: Path) -> Optional[Dict[str, Any]]:
    """
    Convert file to OpenAI-compatible image_url payload.
    We prefer native bytes for jpg/png/webp. For others, try Pillow convert to JPG.
    Returns dict payload or None (if cannot load).
    """
    ext = path.suffix.lower().lstrip(".")
    if ext == "jfif":
        ext = "jpeg"

    raw: Optional[bytes] = None
    mime = None

    try:
        if ext in {"jpg", "jpeg", "png", "webp"}:
            raw = path.read_bytes()
            mime = ext
        else:
            # best-effort convert via Pillow
            from PIL import Image  # lazy import

            with Image.open(path) as img:
                img = img.convert("RGB")
                out = Path(path).with_suffix(".jpg")
                # write to memory only
                import io

                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85, optimize=True)
                raw = buf.getvalue()
                mime = "jpeg"
    except Exception:
        return None

    if not raw or not mime:
        return None

    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/{mime};base64,{_encode_bytes(raw)}"},
    }


def _get_openai_client():
    """
    Lazy import so tests/dry-run don't require OpenAI client availability.
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError(f"OpenAI SDK not available: {e}") from e

    # OpenAI() reads OPENAI_API_KEY from env by default
    return OpenAI()


def analyze_item_hybrid(image_paths: List[Path], text_context: str, *, model: str, max_images: int) -> Optional[Dict[str, Any]]:
    """
    Calls OpenAI vision+text (or text only) and returns parsed JSON dict.
    """
    mode = "VISION+TEXT" if image_paths else "ONLY-TEXT"
    logger.info("      -> AI mode: %s (%d images, %d text chars)", mode, len(image_paths), len(text_context))

    prompt = (
        "Analysiere dieses Kleidungsstück.\n"
        f"TEXT-DATEN: '{text_context}'\n"
        "Nutze STRIKT die Mode-Ontologie IDs (cat_..., etc.).\n"
        "GIB NUR EIN VALIDES JSON ZURÜCK:\n"
        "{\n"
        '  "brand": "Marke", "category": "cat_...", "name": "Produktname",\n'
        '  "color_primary": "Farbe", "material_main": "Material",\n'
        '  "fit": "Passform", "collar": "Kragenform", "price": "Preis",\n'
        '  "vision_description": "Detaillierte Analyse"\n'
        "}"
    )

    content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

    # Attach up to N images (best-effort)
    attached = 0
    for p in image_paths:
        if attached >= max_images:
            break
        payload = _image_to_data_url(p)
        if payload is None:
            continue
        content.append(payload)
        attached += 1

    client = _get_openai_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )
        txt = resp.choices[0].message.content
        return json.loads(txt)
    except Exception as e:
        logger.error("      [!] OpenAI error: %s", e)
        return None


def _db_has_image_path(conn: sqlite3.Connection, user: str, image_path: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT id FROM items WHERE user_id = ? AND image_path = ? LIMIT 1", (user, image_path))
    return cur.fetchone() is not None


def _robust_rmtree(path: Path) -> None:
    """
    Robust delete on Windows (handles read-only files).
    """
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
    """
    Robust move folder with Windows-lock retries.
    If dst exists, remove it first (best-effort).
    """
    for i in range(retries):
        try:
            if dst.exists():
                _robust_rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return True
        except PermissionError:
            logger.warning("      [!] PermissionError, retrying (%d/%d)...", i + 1, retries)
            time.sleep(delay_s)
        except Exception as e:
            logger.error("      [!] Move failed: %s", e)
            break
    return False


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Wardrobe Studio ingestion (run-registry instrumented).")

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
    ap.add_argument("--user", type=str, default="", help="Only ingest for this user (andreas|karen). Empty = all.")
    ap.add_argument("--max-items", type=int, default=0, help="Stop after N processed items (0 = unlimited).")
    ap.add_argument("--dry-run", action="store_true", help="No OpenAI, no DB writes, no moves.")
    ap.add_argument("--model", type=str, default=os.environ.get("WARDROBE_INGEST_MODEL", "gpt-4o-mini"))
    ap.add_argument("--max-images", type=int, default=3, help="Max images sent to OpenAI per item (default 3).")
    ap.add_argument("--force", action="store_true", help="Process even if dest exists / DB has same image_path.")
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    settings.reload_settings()
    ensure_schema()

    args = parse_args(argv)
    input_dir = Path(args.input_dir)
    archive_dir = Path(args.archive_dir)

    meta = {
        "input_dir": str(input_dir),
        "archive_dir": str(archive_dir),
        "user": args.user or None,
        "max_items": args.max_items,
        "dry_run": bool(args.dry_run),
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
        users: List[str]
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

        # DB connection for idempotence checks (read-only-ish)
        conn = sqlite3.connect(str(settings.DB_PATH), timeout=5)
        conn.row_factory = sqlite3.Row
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
                    run.event("item.start", data={"user": user, "item": item_name})

                    # gather content
                    img_files = _list_image_files(item_dir)
                    txt_context = _read_text_files(item_dir)

                    if not img_files and not txt_context:
                        stats.skipped += 1
                        run.event("item.skip_empty", level="WARN", data={"user": user, "item": item_name})
                        continue

                    dest_rel = f"{user}/{item_name}"
                    dest_dir = archive_dir / user / item_name

                    # idempotence: if DB already has this image_path, skip (unless --force)
                    if (not args.force) and _db_has_image_path(conn, user, dest_rel):
                        stats.skipped += 1
                        run.event("item.skip_already_ingested", level="WARN", data={"user": user, "item": item_name, "image_path": dest_rel})
                        continue

                    # dry-run: simulate
                    if args.dry_run:
                        stats.processed += 1
                        stats.ok += 1
                        run.event(
                            "item.dry_run",
                            data={
                                "user": user,
                                "item": item_name,
                                "images": len(img_files),
                                "text_chars": len(txt_context),
                                "would_move_to": str(dest_dir),
                                "would_insert_image_path": dest_rel,
                            },
                        )
                        continue

                    # analyze via OpenAI
                    stats.processed += 1
                    run.event("item.analyze.start", data={"user": user, "item": item_name, "images": len(img_files), "text_chars": len(txt_context)})
                    data = analyze_item_hybrid(img_files, txt_context, model=args.model, max_images=args.max_images)
                    if not data:
                        stats.failed += 1
                        run.event("item.analyze.failed", level="ERROR", data={"user": user, "item": item_name})
                        continue

                    # close file handles before move (Windows)
                    gc.collect()

                    # move folder first (so DB never points to missing images)
                    if dest_dir.exists() and not args.force:
                        stats.failed += 1
                        run.event("item.dest_exists", level="ERROR", data={"user": user, "item": item_name, "dest_dir": str(dest_dir)})
                        continue

                    ok_move = robust_move(item_dir, dest_dir)
                    if not ok_move:
                        stats.failed += 1
                        run.event("item.move.failed", level="ERROR", data={"user": user, "item": item_name, "dest_dir": str(dest_dir)})
                        continue

                    # write DB entry (saga: rollback move on DB failure)
                    try:
                        conn_w = sqlite3.connect(str(settings.DB_PATH), timeout=5)
                        try:
                            cur = conn_w.cursor()
                            cur.execute(
                                """
                                INSERT INTO items (
                                    user_id, name, brand, category, color_primary,
                                    color_variant, needs_review,
                                    material_main, fit, collar, price, vision_description, image_path
                                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                                """,
                                (
                                    user,
                                    (data.get("name") or item_name),
                                    data.get("brand"),
                                    data.get("category"),
                                    data.get("color_primary"),
                                    None,
                                    0,
                                    data.get("material_main"),
                                    data.get("fit"),
                                    data.get("collar"),
                                    data.get("price"),
                                    data.get("vision_description"),
                                    dest_rel,
                                ),
                            )
                            conn_w.commit()
                        finally:
                            conn_w.close()

                        stats.ok += 1
                        run.event("item.ok", data={"user": user, "item": item_name, "image_path": dest_rel})

                    except Exception as e:
                        stats.failed += 1
                        run.event("item.db_insert_failed", level="ERROR", message=str(e), data={"user": user, "item": item_name})

                        # rollback: move folder back into input
                        try:
                            rollback_ok = robust_move(dest_dir, item_dir)
                            run.event("item.rollback_move", data={"ok": rollback_ok, "user": user, "item": item_name})
                        except Exception as e2:
                            run.event("item.rollback_move_failed", level="ERROR", message=str(e2), data={"user": user, "item": item_name})

            # end loop
        finally:
            conn.close()

        dur_ms = int((_now_s() - t0) * 1000)
        summary = f"scanned={stats.scanned} processed={stats.processed} ok={stats.ok} failed={stats.failed} skipped={stats.skipped} dry_run={args.dry_run} dur_ms={dur_ms}"
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
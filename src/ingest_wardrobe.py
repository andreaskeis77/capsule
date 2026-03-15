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
import logging
import os
import sqlite3
import time
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
from src.ingest_item_fs import robust_move, robust_rmtree as _robust_rmtree
from src.ingest_item_io import (
    VALID_IMAGE_EXTS,
    VALID_TEXT_EXTS,
    encode_bytes as _encode_bytes,
    folder_signature_fingerprint as _folder_signature_fingerprint,
    image_to_data_url as _image_to_data_url,
    list_image_files as _list_image_files,
    read_text_files as _read_text_files,
)
from src.ingest_item_runner import Stats, build_run_meta, run_ingest
from src.run_registry import start_run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("WardrobeIngest")

VALID_USERS = {"andreas", "karen"}



def _now_s() -> float:
    return time.perf_counter()


def _connect_ro() -> sqlite3.Connection:
    return connect_db(settings.DB_PATH)


def _with_write_connection(operation, *args, **kwargs):
    return run_with_connection(settings.DB_PATH, operation, *args, **kwargs)


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

    meta = build_run_meta(args, input_dir=input_dir, archive_dir=archive_dir, quarantine_dir=quarantine_dir)
    run = start_run("ingest", "wardrobe_ingest", meta=meta)
    t0 = _now_s()

    return run_ingest(
        args=args,
        run=run,
        t0=t0,
        now_s=_now_s,
        input_dir=input_dir,
        archive_dir=archive_dir,
        quarantine_dir=quarantine_dir,
        valid_users=VALID_USERS,
        connect_ro=_connect_ro,
        write_connection=_with_write_connection,
        list_image_files=_list_image_files,
        read_text_files=_read_text_files,
        folder_signature_fingerprint=_folder_signature_fingerprint,
        db_get_by_fingerprint=_db_get_by_fingerprint,
        db_claim_pending=_db_claim_pending,
        db_mark_ok=_db_mark_ok,
        db_mark_failed=_db_mark_failed,
        robust_move=robust_move,
        analyze_item_hybrid=analyze_item_hybrid,
        fake_ai=_fake_ai,
    )


if __name__ == "__main__":
    raise SystemExit(main())

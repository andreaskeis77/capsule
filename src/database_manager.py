from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from src import settings
from src.db_schema import ensure_schema

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")


def _resolve_db_path(db_path: Optional[Path | str] = None) -> Path:
    if db_path is not None:
        return Path(db_path)
    env = os.environ.get("WARDROBE_DB_PATH", "").strip()
    if env:
        return Path(env)
    return Path(settings.DB_PATH)


def reset_database(db_path: Optional[Path | str] = None) -> Path:
    target = _resolve_db_path(db_path)

    if target.exists():
        try:
            target.unlink()
            print("[*] Alte DB gelöscht.")
        except PermissionError:
            print("[!] Fehler: DB gesperrt.")
            raise

    target.parent.mkdir(parents=True, exist_ok=True)
    ensure_schema(target)
    print("[OK] Datenbank neu erstellt.")
    return target


if __name__ == "__main__":
    reset_database()

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Optional

from src.db_schema import ensure_schema

DEFAULT_DB = Path("03_database") / "wardrobe.db"


def _db_path() -> Path:
    env = os.environ.get("WARDROBE_DB_PATH", "").strip()
    return Path(env) if env else DEFAULT_DB


def update_schema(db_path: Optional[Path] = None) -> List[str]:
    resolved = Path(db_path) if db_path is not None else _db_path()
    return ensure_schema(resolved)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ensure Wardrobe DB schema is current.")
    ap.add_argument("--db-path", type=str, default="", help="Optional explicit DB path")
    args = ap.parse_args(argv)

    target = Path(args.db_path) if args.db_path else _db_path()
    changes = update_schema(target)

    if changes:
        print(f"[OK] Schema updated in {target}.")
        for change in changes:
            print(f" - {change}")
    else:
        print(f"[OK] Schema already up to date in {target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

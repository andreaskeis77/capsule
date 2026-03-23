#!/usr/bin/env python3
"""
Project Data Snapshot
Captures data-layer state for Wardrobe Studio:
- DB exists? size? sqlite version?
- list tables + row counts
- schema for key tables (PRAGMA table_info)
- basic item stats (per user counts)
- image folder stats (counts, top folders)
- ontology files metadata (mtime, sha256) for yaml/md in ontology/

Outputs a readable markdown report.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from tools.ops_common import fmt_bytes, sha256_file, utc_now_iso, write_text
except Exception:  # pragma: no cover - direct script execution fallback
    from ops_common import fmt_bytes, sha256_file, utc_now_iso, write_text  # type: ignore


def sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]


def table_rowcount(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0]) if row else 0


def table_info(conn: sqlite3.Connection, table: str) -> List[Tuple]:
    return conn.execute(f"PRAGMA table_info({table})").fetchall()


def image_stats(img_dir: Path, max_folders: int = 25) -> Tuple[int, int, List[Tuple[str, int]]]:
    if not img_dir.exists():
        return 0, 0, []

    folder_counts: Dict[str, int] = {}
    image_count = 0
    folder_count = 0

    for root, _dirs, files in os.walk(img_dir):
        rel = str(Path(root).relative_to(img_dir)).replace("\\", "/")
        imgs = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        if imgs:
            folder_count += 1
            folder_counts[rel] = len(imgs)
            image_count += len(imgs)

    top = sorted(folder_counts.items(), key=lambda x: x[1], reverse=True)[:max_folders]
    return folder_count, image_count, top


def ontology_stats(onto_dir: Path) -> List[Tuple[str, str, str, int]]:
    out: List[Tuple[str, str, str, int]] = []
    if not onto_dir.exists():
        return out

    files: list[Path] = []
    for path in onto_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in (".md", ".yaml", ".yml"):
            files.append(path)
    files.sort(key=lambda p: str(p).lower())

    for path in files:
        st = path.stat()
        mtime = dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).replace(microsecond=0).isoformat()
        out.append((str(path.relative_to(onto_dir)).replace("\\", "/"), mtime, sha256_file(path), int(st.st_size)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--out", required=True, help="Output markdown path")
    ap.add_argument("--db", default="03_database/wardrobe.db", help="DB relative path")
    ap.add_argument("--images", default="02_wardrobe_images", help="Images dir relative path")
    ap.add_argument("--ontology", default="ontology", help="Ontology dir relative path")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_path = Path(args.out).resolve()
    db_path = (root / args.db).resolve()
    img_dir = (root / args.images).resolve()
    onto_dir = (root / args.ontology).resolve()

    lines: List[str] = []
    lines.append("# Wardrobe Studio – Data Snapshot\n\n")
    lines.append(f"- generated_utc: {utc_now_iso()}\n")
    lines.append(f"- repo_root: {root}\n")
    lines.append(f"- db_path: {db_path}\n")
    lines.append(f"- images_dir: {img_dir}\n")
    lines.append(f"- ontology_dir: {onto_dir}\n\n")
    lines.append("---\n\n")

    lines.append("## Database\n\n")
    if not db_path.exists():
        lines.append(f"❌ DB not found: `{db_path}`\n\n")
    else:
        st = db_path.stat()
        lines.append(f"- exists: yes\n")
        lines.append(f"- size: {fmt_bytes(int(st.st_size))}\n")
        lines.append(
            f"- mtime_utc: {dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).replace(microsecond=0).isoformat()}\n"
        )
        lines.append(f"- sha256: `{sha256_file(db_path)}`\n\n")

        try:
            conn = sqlite3.connect(str(db_path))
            rows = conn.execute("select sqlite_version()").fetchone()
            lines.append(f"- sqlite_version: {rows[0] if rows else 'unknown'}\n\n")

            tables = sqlite_tables(conn)
            lines.append("### Tables (row counts)\n\n")
            lines.append("| table | rows |\n|---|---:|\n")
            for table in tables:
                try:
                    count = table_rowcount(conn, table)
                except Exception:
                    count = -1
                lines.append(f"| `{table}` | {count} |\n")
            lines.append("\n")

            if "items" in tables:
                lines.append("### Schema: `items`\n\n")
                info = table_info(conn, "items")
                lines.append("| cid | name | type | notnull | dflt_value | pk |\n|---:|---|---|---:|---|---:|\n")
                for cid, name, typ, notnull, dflt, pk in info:
                    lines.append(f"| {cid} | `{name}` | `{typ}` | {notnull} | `{dflt}` | {pk} |\n")
                lines.append("\n")

                lines.append("### Items per user_id\n\n")
                try:
                    rows = conn.execute("SELECT user_id, COUNT(*) FROM items GROUP BY user_id ORDER BY user_id").fetchall()
                    lines.append("| user_id | count |\n|---|---:|\n")
                    for user_id, count in rows:
                        lines.append(f"| `{user_id}` | {int(count)} |\n")
                    lines.append("\n")
                except Exception as exc:
                    lines.append(f"_ERROR querying items per user: {exc}_\n\n")

            conn.close()
        except Exception as exc:
            lines.append(f"❌ ERROR opening DB: {exc}\n\n")

    lines.append("---\n\n")

    lines.append("## Images\n\n")
    folder_count, image_count, top = image_stats(img_dir)
    if not img_dir.exists():
        lines.append(f"❌ images_dir not found: `{img_dir}`\n\n")
    else:
        lines.append(f"- folders_with_images: {folder_count}\n")
        lines.append(f"- total_images: {image_count}\n\n")
        lines.append("### Top folders by image count\n\n")
        lines.append("| folder | images |\n|---|---:|\n")
        for rel, count in top:
            lines.append(f"| `{rel}` | {count} |\n")
        lines.append("\n")

    lines.append("---\n\n")

    lines.append("## Ontology files\n\n")
    onto = ontology_stats(onto_dir)
    if not onto_dir.exists():
        lines.append(f"❌ ontology_dir not found: `{onto_dir}`\n\n")
    else:
        lines.append(f"- files: {len(onto)}\n\n")
        lines.append("| path | mtime_utc | size | sha256 |\n|---|---|---:|---|\n")
        for rel, mtime, digest, size in onto:
            lines.append(f"| `{rel}` | {mtime} | {size} | `{digest}` |\n")
        lines.append("\n")

    write_text(out_path, "".join(lines))
    print(f"Data snapshot written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

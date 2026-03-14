from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("WardrobeControl")

LEGACY_FIELDS = ("category", "color_primary", "material_main", "fit", "collar")


def _read_yaml_mapping_file(path: Optional[Path], *, label: str) -> Dict[str, Any]:
    if not path or not Path(path).exists():
        return {}

    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception(f"Failed to load {label}: {exc}", extra={"request_id": "-"})
        return {}

    if isinstance(data, dict):
        return data
    return {}


def load_overrides(path: Optional[Path]) -> Dict[str, Dict[str, str]]:
    data = _read_yaml_mapping_file(path, label="ontology overrides")
    if not data:
        return {}

    out: Dict[str, Dict[str, str]] = {}
    for key, value in data.items():
        if key == "version":
            continue
        if isinstance(value, dict):
            out[str(key)] = {str(source): str(target) for source, target in value.items()}

    logger.info(f"Loaded ontology overrides from {path}", extra={"request_id": "-"})
    return out


def load_color_lexicon(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    data = _read_yaml_mapping_file(path, label="color lexicon")
    if not data:
        return {}

    out: Dict[str, Dict[str, Any]] = {}
    for key, value in data.items():
        if key == "version":
            continue
        if isinstance(value, dict):
            out[str(key)] = dict(value)

    logger.info(
        f"Loaded color lexicon from {path} ({len(out)} entries)",
        extra={"request_id": "-"},
    )
    return out


def empty_legacy_values() -> Dict[str, List[str]]:
    return {field: [] for field in LEGACY_FIELDS}


def load_legacy_values(db_path: Path) -> Dict[str, List[str]]:
    legacy = empty_legacy_values()

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        try:
            for field in LEGACY_FIELDS:
                cur.execute(
                    f"SELECT DISTINCT {field} FROM items WHERE {field} IS NOT NULL AND TRIM({field}) != ''"
                )
                values = [row[0] for row in cur.fetchall() if isinstance(row[0], str)]
                legacy[field] = sorted(set(value.strip() for value in values if value and value.strip()))
        finally:
            conn.close()
    except Exception:
        return legacy

    return legacy

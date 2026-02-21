# FILE: src/settings.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Set

from dotenv import load_dotenv

# Project root (repo root)
BASE_DIR = Path(__file__).resolve().parents[1]

# Load .env once (default: does NOT override already-set env vars)
load_dotenv(BASE_DIR / ".env")


def _get_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_bool(name: str, default: str = "0") -> bool:
    return _get_str(name, default) in {"1", "true", "True", "yes", "YES", "on", "ON"}


def _get_int(name: str, default: str) -> int:
    return int(_get_str(name, default))


def _get_float(name: str, default: str) -> float:
    return float(_get_str(name, default))


def _norm_path(raw: str, default: Path) -> Path:
    """
    Normalize env paths:
    - empty => default
    - relative => relative to BASE_DIR (stable, independent of current working dir)
    - expanduser + resolve (strict=False)
    """
    raw = (raw or "").strip()
    p = Path(raw) if raw else default
    p = p.expanduser()
    if not p.is_absolute():
        p = BASE_DIR / p
    return p.resolve()


def _load_from_env() -> Dict[str, Any]:
    wardrobe_env = _get_str("WARDROBE_ENV", "dev").lower()
    debug = _get_bool("WARDROBE_DEBUG", "0")
    log_level = _get_str("WARDROBE_LOG_LEVEL", "INFO").upper()

    # Security
    allow_local_noauth = _get_bool("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    api_key = _get_str("WARDROBE_API_KEY", "")

    # Storage paths
    db_path = _norm_path(_get_str("WARDROBE_DB_PATH", ""), BASE_DIR / "03_database" / "wardrobe.db")
    img_dir = _norm_path(_get_str("WARDROBE_IMG_DIR", ""), BASE_DIR / "02_wardrobe_images")

    # Trash (for delete safety)
    trash_dir = _norm_path(_get_str("WARDROBE_TRASH_DIR", ""), BASE_DIR / "04_user_data" / "trash_images")

    # Logs (logging_config also reads env directly; keep these for convenience)
    log_dir = _norm_path(_get_str("WARDROBE_LOG_DIR", ""), BASE_DIR / "04_user_data" / "logs")
    log_file = _norm_path(_get_str("WARDROBE_LOG_FILE", ""), log_dir / "api.log")

    # Images
    max_image_mb = _get_int("WARDROBE_MAX_IMAGE_MB", "8")
    max_image_bytes = max(0, max_image_mb) * 1024 * 1024
    image_max_dim = _get_int("WARDROBE_IMAGE_MAX_DIM", "1600")
    image_jpeg_quality = _get_int("WARDROBE_IMAGE_JPEG_QUALITY", "85")
    store_original = _get_bool("WARDROBE_STORE_ORIGINAL", "0")

    # Optional mounting control (api_main may or may not use this yet)
    mount_flask = _get_bool("WARDROBE_MOUNT_FLASK", "1")

    # Ontology
    ontology_mode = _get_str("WARDROBE_ONTOLOGY_MODE", "off").lower()
    if ontology_mode not in {"off", "soft", "strict"}:
        ontology_mode = "off"

    ontology_allow_legacy = _get_bool("WARDROBE_ONTOLOGY_ALLOW_LEGACY", "1")
    ontology_fuzzy_threshold = _get_float("WARDROBE_ONTOLOGY_FUZZY_THRESHOLD", "0.92")
    ontology_suggest_threshold = _get_float("WARDROBE_ONTOLOGY_SUGGEST_THRESHOLD", "0.78")
    ontology_dir = _norm_path(_get_str("WARDROBE_ONTOLOGY_DIR", ""), BASE_DIR / "ontology")

    ontology_overrides_file = _norm_path(
        _get_str("WARDROBE_ONTOLOGY_OVERRIDES_FILE", ""), ontology_dir / "ontology_overrides.yaml"
    )
    ontology_color_lexicon_file = _norm_path(
        _get_str("WARDROBE_ONTOLOGY_COLOR_LEXICON_FILE", ""), ontology_dir / "color_lexicon.yaml"
    )

    tolerant_raw = _get_str("WARDROBE_ONTOLOGY_TOLERANT_FIELDS", "color_primary")
    ontology_tolerant_fields: Set[str] = {f.strip() for f in tolerant_raw.split(",") if f.strip()}

    # Expose a stable set of module-level settings (plus a few compat aliases)
    return {
        "WARDROBE_ENV": wardrobe_env,
        "DEBUG": debug,
        "LOG_LEVEL": log_level,
        "ALLOW_LOCAL_NOAUTH": allow_local_noauth,
        "API_KEY": api_key,
        "DB_PATH": db_path,
        "IMG_DIR": img_dir,
        "TRASH_DIR": trash_dir,
        "LOG_DIR": log_dir,
        "LOG_FILE": log_file,
        "MAX_IMAGE_MB": max_image_mb,
        "MAX_IMAGE_BYTES": max_image_bytes,
        "IMAGE_MAX_DIM": image_max_dim,
        "IMAGE_JPEG_QUALITY": image_jpeg_quality,
        "STORE_ORIGINAL": store_original,
        "MOUNT_FLASK": mount_flask,
        "ONTOLOGY_MODE": ontology_mode,
        "ONTOLOGY_ALLOW_LEGACY": ontology_allow_legacy,
        "ONTOLOGY_FUZZY_THRESHOLD": ontology_fuzzy_threshold,
        "ONTOLOGY_SUGGEST_THRESHOLD": ontology_suggest_threshold,
        "ONTOLOGY_DIR": ontology_dir,
        "ONTOLOGY_OVERRIDES_FILE": ontology_overrides_file,
        "ONTOLOGY_COLOR_LEXICON_FILE": ontology_color_lexicon_file,
        "ONTOLOGY_TOLERANT_FIELDS": ontology_tolerant_fields,
        # Compat aliases (falls irgendwo historisch verwendet)
        "FUZZY_THRESHOLD": ontology_fuzzy_threshold,
        "SUGGEST_THRESHOLD": ontology_suggest_threshold,
        "TRASH_ROOT": trash_dir,
    }


def reload_settings() -> None:
    """
    Re-read environment variables and update module-level globals.
    Useful for tests and for code paths that change env at runtime.
    """
    cfg = _load_from_env()
    globals().update(cfg)


# Load settings once at import, but allow reload via reload_settings()
reload_settings()
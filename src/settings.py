# FILE: src/settings.py
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() in {"1", "true", "True", "yes", "YES"}


def _get_int(name: str, default: str) -> int:
    return int(os.environ.get(name, default).strip())


def _get_float(name: str, default: str) -> float:
    return float(os.environ.get(name, default).strip())


WARDROBE_ENV = os.environ.get("WARDROBE_ENV", "dev").strip().lower()
DEBUG = _get_bool("WARDROBE_DEBUG", "0")
LOG_LEVEL = os.environ.get("WARDROBE_LOG_LEVEL", "INFO").strip().upper()

# Security
ALLOW_LOCAL_NOAUTH = _get_bool("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
API_KEY = os.environ.get("WARDROBE_API_KEY", "").strip()

# Storage paths
DB_PATH = Path(os.environ.get("WARDROBE_DB_PATH", str(BASE_DIR / "03_database" / "wardrobe.db")))
IMG_DIR = Path(os.environ.get("WARDROBE_IMG_DIR", str(BASE_DIR / "02_wardrobe_images")))
TRASH_DIR = Path(os.environ.get("WARDROBE_TRASH_DIR", str(BASE_DIR / "04_user_data" / "trash_images")))

# Logs
LOG_DIR = BASE_DIR / "04_user_data" / "logs"
LOG_FILE = LOG_DIR / "api.log"

# Images
MAX_IMAGE_MB = _get_int("WARDROBE_MAX_IMAGE_MB", "8")
MAX_IMAGE_BYTES = MAX_IMAGE_MB * 1024 * 1024
IMAGE_MAX_DIM = _get_int("WARDROBE_IMAGE_MAX_DIM", "1600")
IMAGE_JPEG_QUALITY = _get_int("WARDROBE_IMAGE_JPEG_QUALITY", "85")

# Ontology validation
ONTOLOGY_MODE = os.environ.get("WARDROBE_ONTOLOGY_MODE", "off").strip().lower()  # off|soft|strict
ONTOLOGY_ALLOW_LEGACY = _get_bool("WARDROBE_ONTOLOGY_ALLOW_LEGACY", "1")
ONTOLOGY_FUZZY_THRESHOLD = _get_float("WARDROBE_ONTOLOGY_FUZZY_THRESHOLD", "0.92")
ONTOLOGY_SUGGEST_THRESHOLD = _get_float("WARDROBE_ONTOLOGY_SUGGEST_THRESHOLD", "0.78")
ONTOLOGY_DIR = Path(os.environ.get("WARDROBE_ONTOLOGY_DIR", str(BASE_DIR / "ontology")))

ONTOLOGY_OVERRIDES_FILE = Path(
    os.environ.get("WARDROBE_ONTOLOGY_OVERRIDES_FILE", str(ONTOLOGY_DIR / "ontology_overrides.yaml"))
)

ONTOLOGY_COLOR_LEXICON_FILE = Path(
    os.environ.get("WARDROBE_ONTOLOGY_COLOR_LEXICON_FILE", str(ONTOLOGY_DIR / "color_lexicon.yaml"))
)

# Fields that should not hard-fail in soft mode (avoid user spam)
ONTOLOGY_TOLERANT_FIELDS = {
    f.strip()
    for f in os.environ.get("WARDROBE_ONTOLOGY_TOLERANT_FIELDS", "color_primary").split(",")
    if f.strip()
}

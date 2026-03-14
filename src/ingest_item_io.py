from __future__ import annotations

import base64
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

VALID_IMAGE_EXTS: Set[str] = {".jpg", ".jpeg", ".png", ".webp", ".jfif", ".heic"}
VALID_TEXT_EXTS: Set[str] = {".txt"}

logger = logging.getLogger("WardrobeIngest")


def encode_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def read_text_files(item_dir: Path, *, valid_text_exts: Optional[Set[str]] = None, log: Optional[logging.Logger] = None) -> str:
    parts: List[str] = []
    allowed_exts = valid_text_exts if valid_text_exts is not None else VALID_TEXT_EXTS
    active_logger = log if log is not None else logger

    for path in sorted(item_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in allowed_exts:
            try:
                parts.append(path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                active_logger.exception("Failed reading text file: %s", path)

    return "\n".join(parts).strip()


def list_image_files(item_dir: Path, *, valid_image_exts: Optional[Set[str]] = None) -> List[Path]:
    allowed_exts = valid_image_exts if valid_image_exts is not None else VALID_IMAGE_EXTS
    images: List[Path] = []
    for path in sorted(item_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in allowed_exts:
            images.append(path)
    return images


def folder_signature_fingerprint(item_dir: Path) -> str:
    """
    Folder signature fingerprint (fast):
      - uses relative paths + file sizes (NOT contents)
      - stable across moves/renames of the outer folder
    """
    entries: List[Dict[str, Any]] = []
    for path in sorted(item_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(item_dir).as_posix()
        except Exception:
            rel = path.name
        try:
            size = path.stat().st_size
        except Exception:
            size = None
        entries.append({"rel": rel, "size": size})

    blob = json.dumps(entries, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def image_to_data_url(path: Path) -> Optional[Dict[str, Any]]:
    ext = path.suffix.lower().lstrip(".")
    if ext == "jfif":
        ext = "jpeg"

    raw: Optional[bytes] = None
    mime: Optional[str] = None

    try:
        if ext in {"jpg", "jpeg", "png", "webp"}:
            raw = path.read_bytes()
            mime = ext
        else:
            from PIL import Image  # lazy import
            import io

            with Image.open(path) as image:
                image = image.convert("RGB")
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG", quality=85, optimize=True)
                raw = buffer.getvalue()
                mime = "jpeg"
    except Exception:
        return None

    if not raw or not mime:
        return None

    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/{mime};base64,{encode_bytes(raw)}"},
    }

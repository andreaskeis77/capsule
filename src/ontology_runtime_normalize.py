from __future__ import annotations

import re


def normalize_runtime_token(value: str) -> str:
    normalized = (value or "").strip().lower()
    if not normalized:
        return ""
    normalized = (
        normalized.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    normalized = re.sub(r"[\(\)\[\]\{\},;:\/\\\|]+", " ", normalized)
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[\s\-]+", " ", normalized).strip()
    normalized = re.sub(r"[^a-z0-9_ ]+", "", normalized)
    return normalized


__all__ = ["normalize_runtime_token"]

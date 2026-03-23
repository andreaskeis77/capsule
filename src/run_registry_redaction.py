from __future__ import annotations

import json
import re
from typing import Any, Dict, Set

REDACT_PLACEHOLDER = "***REDACTED***"

# Key names are normalized to lowercase snake-like tokens before matching.
_SENSITIVE_KEY_MARKERS: Set[str] = {
    "api_key",
    "openai_api_key",
    "authorization",
    "bearer",
    "bearer_token",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "password",
    "cookie",
    "session",
    "private_key",
}


def normalize_key_name(key: Any) -> str:
    text = str(key)
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def is_sensitive_key_name(key: Any) -> bool:
    normalized = normalize_key_name(key)
    return any(marker in normalized for marker in _SENSITIVE_KEY_MARKERS)


def redact_for_storage(obj: Any) -> Any:
    """
    Recursively redact secrets from dict/list structures based on key names.

    - dict keys that look sensitive are replaced with REDACT_PLACEHOLDER
    - nested structures are handled recursively
    """
    if obj is None:
        return None

    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for key, value in obj.items():
            if is_sensitive_key_name(key):
                out[str(key)] = REDACT_PLACEHOLDER
            else:
                out[str(key)] = redact_for_storage(value)
        return out

    if isinstance(obj, (list, tuple)):
        return [redact_for_storage(value) for value in obj]

    return obj


def safe_json_dumps(obj: Any) -> str:
    """
    JSON serializer used for meta_json/data_json.
    Applies secret redaction first.
    """
    obj = redact_for_storage(obj)
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        return json.dumps({"_unserializable": str(obj)}, ensure_ascii=False, separators=(",", ":"))

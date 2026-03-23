# FILE: src/settings.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.runtime_config import load_module_settings
from src.runtime_env import (
    BASE_DIR,
    get_env_bool as _runtime_get_bool,
    get_env_float as _runtime_get_float,
    get_env_int as _runtime_get_int,
    get_env_str as _runtime_get_str,
    normalize_env_path,
)



def _get_str(name: str, default: str = "") -> str:
    return _runtime_get_str(name, default)



def _get_bool(name: str, default: str = "0") -> bool:
    return _runtime_get_bool(name, default)



def _get_int(name: str, default: str) -> int:
    return _runtime_get_int(name, default)



def _get_float(name: str, default: str) -> float:
    return _runtime_get_float(name, default)



def _norm_path(raw: str, default: Path) -> Path:
    return normalize_env_path(raw, default=default, base_dir=BASE_DIR)



def _load_from_env() -> Dict[str, Any]:
    return load_module_settings()



def reload_settings() -> None:
    """
    Re-read environment variables and update module-level globals.

    Useful for tests and for code paths that change env at runtime.
    """
    globals().update(_load_from_env())


# Load settings once at import, but allow reload via reload_settings()
reload_settings()

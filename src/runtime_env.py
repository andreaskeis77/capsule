from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]

_TRUE_VALUES = {"1", "true", "True", "yes", "YES", "on", "ON"}


def ensure_project_root_on_syspath(start_file: str | Path | None = None) -> Path:
    """
    Ensure the repository root is on sys.path.

    This keeps `python src/server_entry.py` and `python -m src.server_entry`
    working consistently.
    """
    if start_file is None:
        project_root = BASE_DIR
    else:
        project_root = Path(start_file).resolve().parents[1]

    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    return project_root



def load_project_dotenv(base_dir: Path | None = None, *, override: bool = False) -> Path:
    """
    Load the project-local .env file once the repository root is known.

    `override=False` preserves already-exported environment variables, which keeps
    CI/tests deterministic and allows explicit shell env values to win.
    """
    project_root = (base_dir or BASE_DIR).resolve()
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path, override=override)
    return dotenv_path



def get_env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()



def get_env_bool(name: str, default: str = "0") -> bool:
    return get_env_str(name, default) in _TRUE_VALUES



def get_env_int(name: str, default: str) -> int:
    return int(get_env_str(name, default))



def get_env_float(name: str, default: str) -> float:
    return float(get_env_str(name, default))



def normalize_env_path(raw: str, *, default: Path, base_dir: Path | None = None) -> Path:
    """
    Normalize paths loaded from environment variables.

    Rules:
    - empty => default
    - expanduser
    - relative => resolve against repo root, not current working directory
    - resolve(strict=False) for stable absolute paths
    """
    project_root = (base_dir or BASE_DIR).resolve()
    raw = (raw or "").strip()
    path_value = Path(raw) if raw else default
    path_value = path_value.expanduser()
    if not path_value.is_absolute():
        path_value = project_root / path_value
    return path_value.resolve()

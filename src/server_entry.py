# FILE: src/server_entry.py
from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

BASE_DIR = Path(__file__).resolve().parents[1]



def _ensure_project_root_on_syspath() -> Path:
    """
    Make sure project root is on sys.path even if this file is executed as a script.

    This prevents `ModuleNotFoundError: No module named src` issues.
    """
    project_root = Path(__file__).resolve().parents[1]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    return project_root



def main() -> None:
    project_root = _ensure_project_root_on_syspath()

    # Imports stay inside main so `python src/server_entry.py` still works before
    # `src` is available on sys.path.
    from src.logging_config import setup_logging
    from src.runtime_config import build_uvicorn_kwargs, load_runtime_config
    from src.runtime_env import load_project_dotenv

    load_project_dotenv(project_root)
    setup_logging(project_root=project_root)

    runtime = load_runtime_config()
    uvicorn.run(runtime.app_import_path, **build_uvicorn_kwargs(runtime))


if __name__ == "__main__":
    main()

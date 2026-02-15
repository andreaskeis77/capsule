# FILE: src/server_entry.py
from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

def _ensure_project_root_on_syspath() -> Path:
    """
    Make sure project root is on sys.path even if this file is executed as a script.
    This prevents 'ModuleNotFoundError: No module named src' issues.
    """
    project_root = Path(__file__).resolve().parents[1]  # .../CapsuleWardrobeRAG
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

def main():
    project_root = _ensure_project_root_on_syspath()

    # Import AFTER sys.path fix
    from src.logging_config import setup_logging

    setup_logging(project_root=project_root)

    host = os.getenv("WARDROBE_HOST", "0.0.0.0")
    port = int(os.getenv("WARDROBE_PORT", "5002"))
    debug = os.getenv("WARDROBE_DEBUG", "0") == "1"

    # log_config=None => uvicorn überschreibt unser File-Logging NICHT
    uvicorn.run(
        "src.api_main:app",
        host=host,
        port=port,
        reload=debug,
        access_log=True,
        use_colors=False,
        log_config=None,
        proxy_headers=True,
    )

if __name__ == "__main__":
    main()

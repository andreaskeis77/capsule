# FILE: src/logging_utils.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

# Backwards-compatible wrapper:
# - older code imports get_logger from here
# - newer code uses src.logging_config.setup_logging
from src.logging_config import setup_logging as _setup_logging, request_id_ctx


def setup_logging(project_root: Optional[Path] = None) -> None:
    """
    Backwards-compatible entrypoint.
    Delegates to src.logging_config.setup_logging.
    """
    _setup_logging(project_root=project_root)


def get_logger(name: str = "wardrobe") -> logging.Logger:
    """
    Backwards-compatible logger getter.
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """
    Optional helper for code that wants to set the request id context.
    """
    request_id_ctx.set(request_id)

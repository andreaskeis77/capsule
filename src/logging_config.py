# FILE: src/logging_config.py
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import contextvars

# request_id per-request via ContextVar (sauber, ohne extra=... überall)
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get("-")
        return True


def setup_logging(project_root: Path | None = None) -> None:
    """
    Idempotent Logging Setup:
    - Console + rotating file logs
    - request_id injected via filter
    - uvicorn loggers propagate to root handlers
    """
    level = os.getenv("WARDROBE_LOG_LEVEL", "INFO").upper()

    if project_root is None:
        # src/.. = project root
        project_root = Path(__file__).resolve().parents[1]

    log_dir = Path(os.getenv("WARDROBE_LOG_DIR", str(project_root / "logs")))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = Path(os.getenv("WARDROBE_LOG_FILE", str(log_dir / "wardrobe.log")))

    root = logging.getLogger()
    root.setLevel(level)

    # --- Idempotenz: wenn schon ein FileHandler auf dieselbe Datei existiert, nicht doppelt hinzufügen
    for h in root.handlers:
        if isinstance(h, RotatingFileHandler):
            try:
                if Path(getattr(h, "baseFilename", "")).resolve() == log_file.resolve():
                    return
            except Exception:
                pass

    fmt = "%(asctime)s %(levelname)s request_id=%(request_id)s %(name)s: %(message)s [%(filename)s:%(lineno)d]"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Console
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(formatter)
    sh.addFilter(RequestIdFilter())

    # Rotating file (10MB x 10 Backups)
    fh = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(formatter)
    fh.addFilter(RequestIdFilter())

    root.addHandler(sh)
    root.addHandler(fh)

    # Uvicorn loggers -> root
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(logger_name)
        lg.handlers = []          # keine eigenen Handler
        lg.propagate = True       # an root weiterreichen
        lg.setLevel(level)

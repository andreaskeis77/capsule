from __future__ import annotations

import inspect
import logging
import os
import shutil
import stat
import time
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger("WardrobeIngest")


ChmodFunc = Callable[[str | bytes | os.PathLike[str] | os.PathLike[bytes], int], None]
SleepFunc = Callable[[float], None]


def robust_rmtree(
    path: Path,
    *,
    chmod_func: ChmodFunc = os.chmod,
    rmtree_func=shutil.rmtree,
) -> None:
    has_onexc = "onexc" in inspect.signature(rmtree_func).parameters

    def _make_writable(p) -> None:
        try:
            chmod_func(p, stat.S_IWRITE)
        except Exception:
            pass

    def _onerror(func, p, exc_info):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    def _onexc(func, p, exc):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    if not path.exists():
        return

    if has_onexc:
        rmtree_func(path, onexc=_onexc)
    else:
        rmtree_func(path, onerror=_onerror)


def robust_move(
    src: Path,
    dst: Path,
    *,
    retries: int = 3,
    delay_s: float = 0.8,
    remove_tree=robust_rmtree,
    move_func=shutil.move,
    sleep_func: SleepFunc = time.sleep,
    log: Optional[logging.Logger] = None,
) -> bool:
    active_logger = log if log is not None else logger

    for i in range(retries):
        try:
            if dst.exists():
                remove_tree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            move_func(str(src), str(dst))
            return True
        except PermissionError:
            active_logger.warning("PermissionError, retrying (%d/%d)...", i + 1, retries)
            sleep_func(delay_s)
        except Exception as e:
            active_logger.error("Move failed: %s", e)
            break
    return False

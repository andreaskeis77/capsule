#!/usr/bin/env python3
# FILE: tools/handoff_make_run.py
from __future__ import annotations

# ---- bootstrap: ensure repo root is importable (so `import src` works from anywhere) ----
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
# ---------------------------------------------------------------------------------------

import argparse
import subprocess
from typing import Any, Dict, List, Tuple

from src import settings
from src.run_registry import start_run


def _truncate(s: str, n: int = 4000) -> str:
    if not s:
        return ""
    return s if len(s) <= n else (s[: n - 3] + "...")


def _default_script_path() -> Path:
    return Path(__file__).with_name("handoff_make.py")


def parse_args(argv: List[str] | None = None) -> Tuple[argparse.Namespace, List[str]]:
    ap = argparse.ArgumentParser(
        description="Run-Registry wrapper for tools/handoff_make.py (records runs/events, then executes)."
    )
    ap.add_argument("--script", type=str, default=str(_default_script_path()), help="Path to underlying handoff_make.py")
    ap.add_argument("--dry-run", action="store_true", help="Do not execute underlying script; only record a run.")
    ap.add_argument("--base", type=str, default="http://127.0.0.1:5002")
    ap.add_argument("--user", type=str, default="karen")
    ap.add_argument("--ids", type=str, default="")
    ap.add_argument(
        "--include-ontology-text",
        action="store_true",
        help="Forward to handoff_make.py if supported (optional).",
    )

    # Pass through any unknown args to the underlying script
    args, extra = ap.parse_known_args(argv)
    return args, extra


def main(argv: List[str] | None = None) -> int:
    args, passthrough = parse_args(argv)

    # Ensure settings reflect current env (tests override env vars)
    settings.reload_settings()

    meta: Dict[str, Any] = {
        "base_url": args.base,
        "user": args.user,
        "ids": args.ids,
        "script": args.script,
        "passthrough": passthrough,
        "dry_run": bool(args.dry_run),
        "cwd": str(Path.cwd()),
    }

    h = start_run("tools", "handoff_make", meta=meta)
    h.event("handoff.wrapper.start", data={"cwd": str(Path.cwd())})

    try:
        if args.dry_run:
            h.event("handoff.wrapper.dry_run", message="Skipping execution (dry-run).")
            h.ok(summary="dry-run ok")
            return 0

        script_path = Path(args.script)
        if not script_path.exists():
            h.event("handoff.wrapper.missing_script", level="ERROR", message=f"Missing: {script_path}")
            h.fail(summary=f"MissingScript: {script_path}")
            return 2

        forward: List[str] = []
        forward += ["--base", args.base]
        forward += ["--user", args.user]
        if args.ids:
            forward += ["--ids", args.ids]
        if args.include_ontology_text:
            forward += ["--include-ontology-text"]
        forward += passthrough

        cmd = [sys.executable, str(script_path), *forward]
        h.event("handoff.exec.start", data={"cmd": cmd})

        proc = subprocess.run(cmd, capture_output=True, text=True)

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        # keep console output visible
        if stdout:
            sys.stdout.write(stdout)
        if stderr:
            sys.stderr.write(stderr)

        h.event(
            "handoff.exec.done",
            data={
                "returncode": proc.returncode,
                "stdout_tail": _truncate(stdout, 2000),
                "stderr_tail": _truncate(stderr, 2000),
            },
        )

        if proc.returncode != 0:
            h.fail(summary=f"handoff_make rc={proc.returncode}")
            return int(proc.returncode)

        h.ok(summary="handoff_make ok")
        return 0

    except Exception as e:
        h.event("handoff.wrapper.exception", level="ERROR", message=str(e))
        h.fail(summary=f"{type(e).__name__}: {e}")
        print(f"[handoff_make_run] ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
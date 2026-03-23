#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    from tools.quality_gate_diagnose import build_diagnosis, write_diagnosis
    from tools.reporting_common import write_json as write_json_report
except Exception:  # pragma: no cover
    build_diagnosis = None  # type: ignore
    write_diagnosis = None  # type: ignore
    write_json_report = None  # type: ignore


def utc_now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


REPO_ROOT = find_repo_root(Path(__file__).resolve().parent.parent)


@dataclass
class StepResult:
    name: str
    command: Sequence[str]
    returncode: int
    duration_s: float
    log_file: str
    required: bool
    status: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    if extra:
        env.update(extra)
    return env


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def http_get(url: str, timeout: float = 3.0) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body[:4000]
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="replace")[:4000]
    except Exception as exc:  # pragma: no cover - defensive path
        return 0, str(exc)


def wait_for_http_200(url: str, timeout_s: float, poll_s: float = 0.5) -> tuple[bool, str]:
    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        code, body = http_get(url, timeout=2.0)
        last = f"code={code} body={body[:300]}"
        if code == 200:
            return True, last
        time.sleep(poll_s)
    return False, last


def run_subprocess(
    name: str,
    command: Sequence[str],
    *,
    cwd: Path,
    env: Optional[Dict[str, str]],
    timeout_s: Optional[int],
    outdir: Path,
    required: bool = True,
) -> StepResult:
    log_file = outdir / f"step_{name}.log"
    started = time.perf_counter()
    with log_file.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"$ {' '.join(command)}\n\n")
        fh.flush()
        proc = subprocess.run(
            list(command),
            cwd=str(cwd),
            env=env,
            stdout=fh,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_s,
        )
    duration_s = time.perf_counter() - started
    return StepResult(
        name=name,
        command=list(command),
        returncode=int(proc.returncode),
        duration_s=round(duration_s, 3),
        log_file=str(log_file.relative_to(cwd)),
        required=required,
        status="ok" if proc.returncode == 0 else ("fail" if required else "warn"),
    )


def tail_file(path: Path, lines: int = 60) -> str:
    if not path.exists():
        return f"(missing: {path})"
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


def write_summary(
    *,
    outdir: Path,
    repo_root: Path,
    steps: Sequence[StepResult],
    server_started: bool,
    base_url: str,
) -> None:
    payload: Dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "base_url": base_url,
        "server_started": server_started,
        "steps": [asdict(step) for step in steps],
        "failed_required_steps": [step.name for step in steps if step.required and step.returncode != 0],
    }
    summary_json_path = outdir / "summary.json"
    if write_json_report is not None:
        write_json_report(summary_json_path, payload)
    else:
        summary_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Tranche A Quality Gates Summary",
        "",
        f"- Generated (UTC): {payload['generated_utc']}",
        f"- Repo root: `{repo_root}`",
        f"- Base URL: `{base_url}`",
        f"- Server started by gate runner: `{server_started}`",
        "",
        "## Steps",
        "",
        "| Step | Status | Return code | Duration (s) | Log file |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for step in steps:
        lines.append(
            f"| {step.name} | {step.status} | {step.returncode} | {step.duration_s:.3f} | `{step.log_file}` |"
        )
    failed = payload["failed_required_steps"]
    lines.extend(
        [
            "",
            "## Result",
            "",
            "- **FAILED**" if failed else "- **OK**",
        ]
    )
    if failed:
        lines.append(f"- Required failed steps: {', '.join(failed)}")
    else:
        lines.append("- All required steps passed.")
    lines.append("")
    (outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    if build_diagnosis is not None and write_diagnosis is not None:
        diagnosis = build_diagnosis(payload, repo_root=repo_root)
        write_diagnosis(outdir, diagnosis)


def start_server(
    *,
    python_exe: str,
    repo_root: Path,
    port: int,
    outdir: Path,
    timeout_s: int,
) -> tuple[subprocess.Popen[str], Any, Any]:
    server_out = outdir / "server.out.log"
    server_err = outdir / "server.err.log"
    env = build_env(
        {
            "WARDROBE_PORT": str(port),
            "WARDROBE_HOST": "127.0.0.1",
            "WARDROBE_DEBUG": "0",
        }
    )

    out_fh = server_out.open("w", encoding="utf-8", newline="\n")
    err_fh = server_err.open("w", encoding="utf-8", newline="\n")
    proc = subprocess.Popen(
        [python_exe, "-m", "src.server_entry"],
        cwd=str(repo_root),
        env=env,
        stdout=out_fh,
        stderr=err_fh,
        text=True,
    )

    ok, last = wait_for_http_200(f"http://127.0.0.1:{port}/healthz", timeout_s=timeout_s)
    if not ok:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        out_fh.close()
        err_fh.close()
        raise RuntimeError(
            "Server readiness failed. "
            f"Last probe: {last}\n--- server.out.log tail ---\n{tail_file(server_out)}\n"
            f"--- server.err.log tail ---\n{tail_file(server_err)}"
        )

    return proc, out_fh, err_fh


def stop_server(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Tranche A quality gates with artifact logs.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--python", dest="python_exe", default=sys.executable)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5012)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--user", default="karen")
    parser.add_argument("--ids", default="112,101,110")
    parser.add_argument("--start-server", action="store_true")
    parser.add_argument("--reuse-server", action="store_true")
    parser.add_argument("--skip-compileall", action="store_true")
    parser.add_argument("--skip-ruff", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-secret-scan", action="store_true")
    parser.add_argument("--skip-live-smoke", action="store_true")
    parser.add_argument("--server-timeout", type=int, default=45)
    parser.add_argument("--step-timeout", type=int, default=900)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    outdir = repo_root / "docs" / "_ops" / "quality_gates" / f"run_{utc_now_stamp()}"
    ensure_dir(outdir)

    if args.start_server and args.reuse_server:
        print("ERROR: --start-server and --reuse-server are mutually exclusive.", file=sys.stderr)
        return 2

    if args.base_url:
        base_url = args.base_url.rstrip("/")
    else:
        base_url = f"http://{args.host}:{args.port}"

    steps: List[StepResult] = []
    server_proc: Optional[subprocess.Popen[str]] = None
    server_out_fh: Any = None
    server_err_fh: Any = None
    server_started = False

    try:
        default_env = build_env()

        if not args.skip_compileall:
            steps.append(
                run_subprocess(
                    "compileall",
                    [args.python_exe, "-m", "compileall", "-q", "src", "tests", "tools"],
                    cwd=repo_root,
                    env=default_env,
                    timeout_s=args.step_timeout,
                    outdir=outdir,
                )
            )

        if not args.skip_ruff:
            steps.append(
                run_subprocess(
                    "ruff_critical",
                    [
                        args.python_exe,
                        "-m",
                        "ruff",
                        "check",
                        "--select",
                        "E9,F63,F7,F82",
                        "src",
                        "tests",
                        "tools",
                    ],
                    cwd=repo_root,
                    env=default_env,
                    timeout_s=args.step_timeout,
                    outdir=outdir,
                )
            )

        if not args.skip_pytest:
            steps.append(
                run_subprocess(
                    "pytest",
                    [args.python_exe, "-m", "pytest", "-q"],
                    cwd=repo_root,
                    env=default_env,
                    timeout_s=args.step_timeout,
                    outdir=outdir,
                )
            )

        if not args.skip_secret_scan:
            steps.append(
                run_subprocess(
                    "secret_scan_tracked",
                    [args.python_exe, "tools/secret_scan.py", "--mode", "tracked"],
                    cwd=repo_root,
                    env=default_env,
                    timeout_s=args.step_timeout,
                    outdir=outdir,
                )
            )

        need_live_smoke = not args.skip_live_smoke
        if need_live_smoke:
            if args.reuse_server:
                ok, probe = wait_for_http_200(f"{base_url}/healthz", timeout_s=5)
                if not ok:
                    raise RuntimeError(
                        f"--reuse-server requested but {base_url}/healthz is not ready. Last probe: {probe}"
                    )
            elif args.start_server:
                if is_port_in_use(args.host, args.port):
                    raise RuntimeError(
                        f"Port {args.port} is already in use on {args.host}. "
                        "Use --reuse-server or choose a different --port."
                    )
                server_proc, server_out_fh, server_err_fh = start_server(
                    python_exe=args.python_exe,
                    repo_root=repo_root,
                    port=args.port,
                    outdir=outdir,
                    timeout_s=args.server_timeout,
                )
                server_started = True
            else:
                ok, probe = wait_for_http_200(f"{base_url}/healthz", timeout_s=5)
                if ok:
                    pass
                elif is_port_in_use(args.host, args.port):
                    raise RuntimeError(
                        f"Port {args.port} is already in use on {args.host}, but {base_url}/healthz is not ready. "
                        f"Last probe: {probe}"
                    )
                else:
                    server_proc, server_out_fh, server_err_fh = start_server(
                        python_exe=args.python_exe,
                        repo_root=repo_root,
                        port=args.port,
                        outdir=outdir,
                        timeout_s=args.server_timeout,
                    )
                    server_started = True

            steps.append(
                run_subprocess(
                    "live_smoke",
                    [
                        args.python_exe,
                        "tools/project_sanity_check.py",
                        "--base",
                        base_url,
                        "--user",
                        args.user,
                        "--ids",
                        args.ids,
                    ],
                    cwd=repo_root,
                    env=default_env,
                    timeout_s=args.step_timeout,
                    outdir=outdir,
                )
            )

    except Exception as exc:
        failure_log = outdir / "runner_failure.log"
        failure_log.write_text(str(exc), encoding="utf-8")
        steps.append(
            StepResult(
                name="runner_failure",
                command=[],
                returncode=2,
                duration_s=0.0,
                log_file=str(failure_log.relative_to(repo_root)),
                required=True,
                status="fail",
            )
        )
    finally:
        if server_proc is not None:
            stop_server(server_proc)
        if server_out_fh is not None:
            server_out_fh.close()
        if server_err_fh is not None:
            server_err_fh.close()

    write_summary(outdir=outdir, repo_root=repo_root, steps=steps, server_started=server_started, base_url=base_url)

    print(f"[INFO] quality gate artifacts: {outdir}")
    failed_required = [step for step in steps if step.required and step.returncode != 0]
    if failed_required:
        print("[FAIL] required steps failed:")
        for step in failed_required:
            print(f" - {step.name} (rc={step.returncode}) -> {step.log_file}")
        return 2

    print("[OK] all required quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

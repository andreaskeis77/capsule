from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = Path("tools")


class TaskRunnerError(RuntimeError):
    pass


def _python_executable() -> str:
    return sys.executable


def _quote(cmd: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def _pytest_command(*extra: str) -> list[str]:
    return [_python_executable(), "-m", "pytest", "-q", *extra]


def _build_runner_command(args: argparse.Namespace) -> list[str]:
    py = _python_executable()

    if args.task == "quality-gates":
        return [py, str(TOOLS_DIR / "run_quality_gates.py")]
    if args.task == "server":
        return [py, "-m", "src.server_entry"]
    if args.task == "test":
        return _pytest_command()
    if args.task == "test-unit":
        return _pytest_command("-m", "unit")
    if args.task == "test-smoke":
        return _pytest_command("-m", "smoke")
    if args.task == "test-contract":
        return _pytest_command("-m", "contract")
    if args.task == "test-integration":
        return _pytest_command("-m", "integration")
    if args.task == "test-report":
        return [py, str(TOOLS_DIR / "test_suite_report.py")]
    if args.task == "handoff":
        return [py, str(TOOLS_DIR / "handoff_make.py")]
    if args.task == "snapshot":
        return [py, str(TOOLS_DIR / "project_data_snapshot.py")]
    if args.task == "audit":
        return [py, str(TOOLS_DIR / "project_audit_dump.py")]
    if args.task == "secret-scan":
        return [py, str(TOOLS_DIR / "secret_scan.py"), "--mode", args.mode]
    if args.task == "release-evidence":
        return [py, str(TOOLS_DIR / "release_evidence.py"), "--release-id", args.release_id]
    if args.task == "ci-summary":
        return [py, str(TOOLS_DIR / "ci_artifact_summary.py")]
    if args.task == "diagnose-gates":
        cmd = [py, str(TOOLS_DIR / "quality_gate_diagnose.py")]
        if args.run_dir:
            cmd.append(args.run_dir)
        else:
            cmd.append(str(Path("docs") / "_ops" / "quality_gates" / args.latest_run))
        return cmd
    if args.task == "ops-index":
        return [py, str(TOOLS_DIR / "ops_report_index.py")]

    raise TaskRunnerError(f"Unsupported task: {args.task}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capsule-dev",
        description="Standardized local entrypoints for capsule development and operations.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved command and exit.")

    sub = parser.add_subparsers(dest="task", required=True)

    sub.add_parser("quality-gates", help="Run the full local quality gate chain.")
    sub.add_parser("server", help="Start the local application entrypoint.")
    sub.add_parser("test", help="Run the full pytest suite.")
    sub.add_parser("test-unit", help="Run tests marked as unit.")
    sub.add_parser("test-smoke", help="Run tests marked as smoke.")
    sub.add_parser("test-contract", help="Run tests marked as contract.")
    sub.add_parser("test-integration", help="Run tests marked as integration.")
    sub.add_parser("test-report", help="Summarize the test suite by file and marker.")
    sub.add_parser("handoff", help="Create a handoff bundle.")
    sub.add_parser("snapshot", help="Create a project data snapshot.")
    sub.add_parser("audit", help="Create a project audit dump.")
    sub.add_parser("ci-summary", help="Summarize CI artifacts.")
    sub.add_parser("ops-index", help="Build an index over quality gate and release evidence artifacts.")

    secret = sub.add_parser("secret-scan", help="Run the tracked or full secret scan.")
    secret.add_argument("--mode", choices=["tracked", "full"], default="tracked")

    release = sub.add_parser("release-evidence", help="Generate release evidence from the latest successful quality gate run.")
    release.add_argument("--release-id", required=True)

    diagnose = sub.add_parser("diagnose-gates", help="Classify and summarize a quality gate run directory.")
    diagnose.add_argument("--run-dir", default=None)
    diagnose.add_argument("--latest-run", default="latest", help="Fallback run directory name inside docs/_ops/quality_gates.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    cmd = _build_runner_command(args)

    if args.dry_run:
        print(_quote(cmd))
        return 0

    completed = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())

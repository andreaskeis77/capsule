from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import tools.task_runner as runner


def _ns(task: str, **kwargs):
    values = {
        "task": task,
        "mode": "tracked",
        "release_id": None,
        "dry_run": False,
        "run_dir": None,
        "latest_run": "run_20260322-100000",
    }
    values.update(kwargs)
    return Namespace(**values)


def test_build_runner_command_diagnose_gates_uses_repo_relative_run_dir(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("diagnose-gates"))
    assert cmd == [
        "python",
        str(Path("tools") / "quality_gate_diagnose.py"),
        str(Path("docs") / "_ops" / "quality_gates" / "run_20260322-100000"),
    ]


def test_build_runner_command_ops_index_points_to_tool(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("ops-index"))
    assert cmd == ["python", str(Path("tools") / "ops_report_index.py")]

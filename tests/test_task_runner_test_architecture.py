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
        "latest_run": "latest",
    }
    values.update(kwargs)
    return Namespace(**values)


def test_build_runner_command_test_smoke_uses_marker(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("test-smoke"))
    assert cmd == ["python", "-m", "pytest", "-q", "-m", "smoke"]


def test_build_runner_command_test_contract_uses_marker(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("test-contract"))
    assert cmd == ["python", "-m", "pytest", "-q", "-m", "contract"]


def test_build_runner_command_test_report_points_to_tool(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("test-report"))
    assert cmd == ["python", str(Path("tools") / "test_suite_report.py")]

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
    }
    values.update(kwargs)
    return Namespace(**values)


def test_build_runner_command_quality_gates_points_to_gate_runner(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("quality-gates"))
    assert cmd == ["python", str(Path("tools") / "run_quality_gates.py")]


def test_build_runner_command_release_evidence_requires_release_id(monkeypatch):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    cmd = runner._build_runner_command(_ns("release-evidence", release_id="v1.0.0"))
    assert cmd == ["python", str(Path("tools") / "release_evidence.py"), "--release-id", "v1.0.0"]


def test_main_dry_run_prints_resolved_command(monkeypatch, capsys):
    monkeypatch.setattr(runner, "_python_executable", lambda: "python")
    rc = runner.main(["--dry-run", "secret-scan", "--mode", "full"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert "tools/secret_scan.py" in out or "tools\\secret_scan.py" in out
    assert "--mode full" in out

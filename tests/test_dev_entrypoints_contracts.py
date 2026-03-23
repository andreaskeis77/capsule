from __future__ import annotations

import json
from pathlib import Path


def test_capsule_cmd_points_to_task_runner():
    content = Path("capsule.cmd").read_text(encoding="utf-8")
    assert "tools\\task_runner.py" in content


def test_vscode_tasks_reference_capsule_cmd():
    payload = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
    labels = {task["label"] for task in payload["tasks"]}
    commands = {task["command"] for task in payload["tasks"]}
    assert "capsule: quality-gates" in labels
    assert any("capsule.cmd quality-gates" in command for command in commands)

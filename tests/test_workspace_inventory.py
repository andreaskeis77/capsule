from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_workspace_inventory_builds_artifacts(tmp_path):
    repo = tmp_path
    (repo / "docs" / "_ops").mkdir(parents=True)
    (repo / "logs").mkdir()
    (repo / "src").mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    (repo / "notes.md").write_text("local note\n", encoding="utf-8")
    (repo / "logs" / "server.log").write_text("hello\n", encoding="utf-8")

    out_dir = repo / "docs" / "_ops" / "workspace_inventory" / "run_test"
    script = Path(__file__).resolve().parents[1] / "tools" / "workspace_inventory.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(repo), "--out-dir", str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert (out_dir / "inventory_summary.md").exists()
    assert (out_dir / "inventory_files.csv").exists()
    assert (out_dir / "cleanup_candidates.csv").exists()
    manifest = json.loads((out_dir / "inventory_manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["files"] >= 3

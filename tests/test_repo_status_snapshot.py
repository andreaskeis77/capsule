from __future__ import annotations

import tools.repo_status_snapshot as snap


def test_build_repo_status_snapshot_handles_missing_git(monkeypatch, tmp_path):
    monkeypatch.setattr(snap, "_run_git", lambda args, root: (127, ""))
    payload = snap.build_repo_status_snapshot(tmp_path)

    assert payload["git"]["branch"] is None
    assert payload["git"]["commit_short"] is None
    assert payload["quality_gates"]["run_count"] == 0


def test_build_repo_status_snapshot_reads_quality_gate_runs(monkeypatch, tmp_path):
    qg = tmp_path / "docs" / "_ops" / "quality_gates"
    (qg / "run_20260323-100000").mkdir(parents=True)
    (qg / "run_20260323-110000").mkdir(parents=True)
    monkeypatch.setattr(snap, "_run_git", lambda args, root: (0, "main" if "abbrev-ref" in args else "abc123"))

    payload = snap.build_repo_status_snapshot(tmp_path)

    assert payload["quality_gates"]["run_count"] == 2
    assert payload["quality_gates"]["latest_run_dir"] == "docs/_ops/quality_gates/run_20260323-110000"

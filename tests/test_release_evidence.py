from __future__ import annotations

import json
from pathlib import Path

from tools import release_evidence as reldoc


def test_build_release_payload_reads_latest_successful_run(tmp_path, monkeypatch):
    repo_root = tmp_path
    qg = repo_root / "docs" / "_ops" / "quality_gates"
    good = qg / "run_20260322-211309"
    bad = qg / "run_20260322-200000"
    good.mkdir(parents=True)
    bad.mkdir(parents=True)

    (bad / "summary.json").write_text(json.dumps({"status": "FAIL"}), encoding="utf-8")
    (good / "summary.json").write_text(json.dumps({"status": "OK"}), encoding="utf-8")

    contract = repo_root / ".github" / "branch-protection.required-checks.json"
    contract.parent.mkdir(parents=True)
    contract.write_text(
        json.dumps(
            {
                "required_status_checks": ["quality-gates / quality-gates"],
                "required_review_count": 1,
                "require_code_owner_reviews": True,
                "require_conversation_resolution": True,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(reldoc, "REPO_ROOT", repo_root)
    monkeypatch.setattr(reldoc, "QUALITY_GATES_DIR", qg)
    monkeypatch.setattr(reldoc, "RELEASES_DIR", repo_root / "docs" / "_ops" / "releases")
    monkeypatch.setattr(reldoc, "BRANCH_PROTECTION_CONTRACT", contract)
    monkeypatch.setenv("CAPSULE_COMMIT", "abc123")

    payload = reldoc.build_release_payload(release_id="v1.2.3")

    assert payload["release_id"] == "v1.2.3"
    assert payload["quality_gate_status"] == "OK"
    assert payload["quality_gate_run_dir"] == "docs/_ops/quality_gates/run_20260322-211309"
    assert payload["commit"] == "abc123"


def test_write_release_evidence_writes_json_and_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(reldoc, "RELEASES_DIR", tmp_path / "docs" / "_ops" / "releases")
    payload = {
        "release_id": "v1.2.3",
        "generated_at_utc": "2026-03-22T00:00:00+00:00",
        "commit": "abc123",
        "quality_gate_status": "OK",
        "quality_gate_run_dir": "docs/_ops/quality_gates/run_20260322-211309",
        "quality_gate_summary_json": "docs/_ops/quality_gates/run_20260322-211309/summary.json",
        "required_status_checks": ["quality-gates / quality-gates"],
        "required_review_count": 1,
        "require_code_owner_reviews": True,
        "require_conversation_resolution": True,
    }

    out_dir = reldoc.write_release_evidence(payload)

    assert (out_dir / "release_evidence.json").exists()
    assert (out_dir / "release_evidence.md").exists()
    assert "v1.2.3" in (out_dir / "release_evidence.md").read_text(encoding="utf-8")

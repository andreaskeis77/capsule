from __future__ import annotations

from tests.support.builders import (
    StepSummary,
    build_branch_protection_contract,
    build_quality_gate_summary,
    repo_relative,
    write_quality_gate_run,
)


def test_repo_relative_normalizes_windows_and_posix_separators():
    assert repo_relative("tools\\run_quality_gates.py") == "tools/run_quality_gates.py"
    assert repo_relative("tools/run_quality_gates.py") == "tools/run_quality_gates.py"


def test_build_quality_gate_summary_carries_failed_steps():
    payload = build_quality_gate_summary(
        status="FAIL",
        failed_required_steps=["pytest"],
        steps=[StepSummary(name="pytest", status="fail", returncode=1)],
    )
    assert payload["status"] == "FAIL"
    assert payload["failed_required_steps"] == ["pytest"]
    assert payload["steps"][0]["name"] == "pytest"


def test_build_branch_protection_contract_has_expected_defaults():
    payload = build_branch_protection_contract()
    assert payload["required_status_checks"] == ["quality-gates / quality-gates"]
    assert payload["required_review_count"] == 1
    assert payload["require_code_owner_reviews"] is True


def test_write_quality_gate_run_writes_summary_files(tmp_path):
    run_dir = tmp_path / "docs" / "_ops" / "quality_gates" / "run_20260322-000000"
    payload = build_quality_gate_summary(status="OK")
    write_quality_gate_run(run_dir, summary=payload)
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "summary.md").exists()

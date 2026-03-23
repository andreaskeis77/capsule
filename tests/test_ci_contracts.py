from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relpath: str) -> str:
    return (REPO_ROOT / relpath).read_text(encoding="utf-8")


def test_quality_gates_workflow_contract():
    text = _read(".github/workflows/quality-gates.yml")
    assert "name: quality-gates" in text
    assert "pull_request:" in text
    assert "workflow_dispatch:" in text
    assert "python ./tools/run_quality_gates.py --start-server" in text
    assert "actions/upload-artifact@v4" in text
    assert "quality-gates-${{ github.run_number }}" in text


def test_ops_nightly_health_workflow_contract():
    text = _read(".github/workflows/ops-nightly-health.yml")
    assert "name: ops-nightly-health" in text
    assert 'cron: "17 2 * * *"' in text
    assert "python ./tools/project_audit_dump.py ." in text
    assert "python ./tools/repo_metrics_bold.py . --scan-mode tracked" in text
    assert "docs/_metrics/" in text

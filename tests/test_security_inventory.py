from __future__ import annotations

import json
from pathlib import Path

from tools import security_inventory as inv


def test_parse_requirements_file_supports_space_separated_entries(tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("fastapi==0.1.0 httpx==0.2.0 pytest==9.0.2\n", encoding="utf-8")

    payload = inv.parse_requirements_file(req)

    assert payload["total"] == 3
    assert payload["pinned"] == 3
    assert payload["unpinned"] == 0
    assert payload["invalid"] == []


def test_gather_security_inventory_reads_controls_and_contract(tmp_path, monkeypatch):
    repo_root = tmp_path
    (repo_root / "tools").mkdir()
    (repo_root / "docs").mkdir()
    (repo_root / ".github" / "workflows").mkdir(parents=True)
    (repo_root / "requirements.txt").write_text("fastapi==0.1.0\nuvicorn==0.1.0\n", encoding="utf-8")
    (repo_root / ".env.example").write_text("WARDROBE_ENV=dev\n", encoding="utf-8")
    (repo_root / "tools" / "secret_scan.py").write_text("print('ok')\n", encoding="utf-8")
    (repo_root / ".github" / "workflows" / "quality-gates.yml").write_text("name: qg\n", encoding="utf-8")
    contract = repo_root / ".github" / "branch-protection.required-checks.json"
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

    monkeypatch.setattr(inv, "REPO_ROOT", repo_root)

    payload = inv.gather_security_inventory(repo_root)

    assert payload["required_controls_present"] is True
    assert payload["requirements"]["pinned"] == 2
    assert payload["branch_protection_contract"]["exists"] is True
    assert payload["branch_protection_contract"]["required_status_checks"] == ["quality-gates / quality-gates"]


def test_render_markdown_contains_core_sections(tmp_path, monkeypatch):
    repo_root = tmp_path
    (repo_root / "requirements.txt").write_text("fastapi==0.1.0\n", encoding="utf-8")
    monkeypatch.setattr(inv, "REPO_ROOT", repo_root)

    payload = inv.gather_security_inventory(repo_root)
    rendered = inv.render_markdown(payload)

    assert "# Security Inventory" in rendered
    assert "## Controls" in rendered
    assert "## Branch Protection Contract" in rendered

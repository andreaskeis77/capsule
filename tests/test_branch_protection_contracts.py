from __future__ import annotations

import json
from pathlib import Path


def test_branch_protection_contract_exists_and_is_well_formed():
    contract_path = Path(".github/branch-protection.required-checks.json")
    assert contract_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    assert contract["version"] >= 1
    assert contract["default_branch"] == "main"
    assert isinstance(contract["required_status_checks"], list)
    assert contract["required_status_checks"]
    assert all(isinstance(name, str) and name.strip() for name in contract["required_status_checks"])
    assert isinstance(contract["required_review_count"], int)
    assert contract["required_review_count"] >= 1
    assert contract["require_code_owner_reviews"] is True
    assert contract["require_conversation_resolution"] is True

from __future__ import annotations

from pathlib import Path


def test_security_documents_and_configs_exist():
    assert Path("docs/SECURITY.md").exists()
    assert Path(".github/dependabot.yml").exists()
    assert Path(".github/workflows/security-hygiene-nightly.yml").exists()

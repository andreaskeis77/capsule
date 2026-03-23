from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "INDEX.md",
    REPO_ROOT / "docs" / "QUICKSTART.md",
    REPO_ROOT / "docs" / "ARCHITECTURE.md",
    REPO_ROOT / "docs" / "HANDOFF_GUIDE.md",
    REPO_ROOT / "docs" / "adr" / "ADR-INDEX.md",
    REPO_ROOT / "docs" / "adr" / "ADR-0012-documentation-and-navigation-hardening.md",
]


def test_required_navigation_docs_exist():
    missing = [str(p.relative_to(REPO_ROOT)) for p in REQUIRED_DOCS if not p.exists()]
    assert not missing, f"missing docs: {missing}"


def test_readme_links_to_core_docs():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for rel in [
        "docs/QUICKSTART.md",
        "docs/ARCHITECTURE.md",
        "docs/DEVELOPER_WORKFLOW.md",
        "docs/RUNBOOK.md",
        "docs/HANDOFF_GUIDE.md",
    ]:
        assert rel in text


def test_docs_index_links_to_core_navigation_targets():
    text = (REPO_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    for rel in [
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "RUNBOOK.md",
        "HANDOFF_GUIDE.md",
        "adr/ADR-INDEX.md",
    ]:
        assert rel in text

# FILE: tests/test_docs_navigation.py
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_links_to_current_core_docs():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for rel in [
        "docs/ARCHITECTURE_REQUIREMENTS_DOSSIER.md",
        "docs/ENGINEERING_MANIFEST.md",
        "docs/RELEASE_MANAGEMENT.md",
        "docs/RELEASE_NOTES.md",
        "docs/RUNBOOK.md",
    ]:
        assert rel in text, f"README should reference {rel}"


def test_readme_mentions_supporting_doc_areas():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for rel in [
        "docs/adr/",
        "docs/history/",
        "docs/gpt/",
    ]:
        assert rel in text, f"README should reference {rel}"


def test_core_docs_exist():
    for rel in [
        "docs/ARCHITECTURE_REQUIREMENTS_DOSSIER.md",
        "docs/ENGINEERING_MANIFEST.md",
        "docs/RELEASE_MANAGEMENT.md",
        "docs/RELEASE_NOTES.md",
    ]:
        assert (REPO_ROOT / rel).exists(), f"Missing core doc: {rel}"


def test_initial_adrs_exist():
    for rel in [
        "docs/adr/ADR-0001-system-context-and-runtime-topology.md",
        "docs/adr/ADR-0002-fastapi-flask-cohost.md",
        "docs/adr/ADR-0003-sqlite-and-filesystem-split.md",
        "docs/adr/ADR-0004-ontology-runtime-and-soft-validation.md",
        "docs/adr/ADR-0005-public-exposure-domain-cloudflare-ngrok.md",
    ]:
        assert (REPO_ROOT / rel).exists(), f"Missing ADR: {rel}"
# FILE: tests/test_ontology_includes_ui_categories.py
from __future__ import annotations

from src import category_map as cm
from src.ontology_runtime import OntologyManager


def test_ontology_contains_all_ui_category_keys():
    onto = OntologyManager.load_from_files()
    ids = {c.get("id") for c in (onto.categories or [])}
    missing = sorted([k for k in cm.ADMIN_ALL_KEYS if k not in ids])
    assert not missing, f"Ontology missing UI categories: {missing}"
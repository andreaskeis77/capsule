import logging
import sqlite3
from types import SimpleNamespace

from src.api_item_review import build_review_items, suggest_color_canonicals


class _Suggestion:
    def __init__(self, canonical: str) -> None:
        self.canonical = canonical


class _OntologyOK:
    def normalize_field(self, field: str, value: str):
        assert field == "color_primary"
        assert value == "navy"
        return SimpleNamespace(suggestions=[_Suggestion("blue"), _Suggestion("midnight-blue")])


class _OntologyFails:
    def normalize_field(self, field: str, value: str):
        raise RuntimeError("boom")



def _row() -> sqlite3.Row:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            color_primary TEXT,
            color_variant TEXT,
            needs_review INTEGER
        )
        """
    )
    conn.execute(
        "INSERT INTO items (id, name, category, color_primary, color_variant, needs_review) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Blue Blazer", "cat_blazer", "blue", "navy", 1),
    )
    return conn.execute("SELECT * FROM items WHERE id = 1").fetchone()



def test_suggest_color_canonicals_returns_empty_without_ontology_or_variant():
    logger = logging.getLogger("test")
    assert suggest_color_canonicals(ontology=None, color_variant="navy", request_id="r1", logger=logger) == []
    assert suggest_color_canonicals(ontology=_OntologyOK(), color_variant=None, request_id="r1", logger=logger) == []



def test_suggest_color_canonicals_returns_canonical_values_when_available():
    logger = logging.getLogger("test")
    assert suggest_color_canonicals(
        ontology=_OntologyOK(), color_variant="navy", request_id="r1", logger=logger
    ) == ["blue", "midnight-blue"]



def test_build_review_items_is_resilient_to_ontology_failures():
    row = _row()
    logger = logging.getLogger("test")
    payloads = build_review_items([row], ontology=_OntologyFails(), request_id="r1", logger=logger)
    assert payloads == [
        {
            "id": 1,
            "name": "Blue Blazer",
            "category": "cat_blazer",
            "color_primary": "blue",
            "color_variant": "navy",
            "needs_review": 1,
            "suggestions": [],
        }
    ]

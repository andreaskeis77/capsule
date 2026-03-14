from __future__ import annotations

import pytest

from src.ontology_runtime import _norm
from src.ontology_runtime_matcher import (
    RuntimeMatchContext,
    index_for_field,
    normalize_runtime_field,
    root_category_suggestions,
    suggest_matches,
)


def _build_context() -> RuntimeMatchContext:
    return RuntimeMatchContext(
        idx_category={_norm("Oberteile"): "cat_tops", _norm("Jacken"): "cat_outerwear"},
        cat_label={"cat_tops": "Oberteile", "cat_outerwear": "Jacken"},
        idx_color={_norm("blue"): "blue", _norm("blau"): "blue", _norm("marine"): "blue"},
        idx_fit={_norm("regular"): "regular", _norm("normal"): "regular"},
        idx_collar={_norm("round_neck"): "round_neck"},
        idx_material={_norm("mat_cotton"): "mat_cotton", _norm("cotton"): "mat_cotton"},
        mat_label={"mat_cotton": "Baumwolle"},
        override={"category": {_norm("tops alt"): "cat_tops"}},
        color_lexicon={_norm("marine"): {"family": "blue", "label": "Marine"}},
        legacy={"category": ["historic_bucket"]},
        category_roots=["cat_tops", "cat_outerwear"],
    )


def test_index_for_field_raises_for_unsupported_field() -> None:
    with pytest.raises(ValueError, match="Unsupported field"):
        index_for_field(field="brand", context=_build_context())


def test_suggest_matches_deduplicates_canonical_values() -> None:
    suggestions = suggest_matches(
        index={
            _norm("blue"): "blue",
            _norm("blau"): "blue",
            _norm("bleu"): "blue",
        },
        label_map=None,
        value="blu",
        normalize=_norm,
        suggest_threshold=0.1,
        limit=5,
    )

    assert [suggestion.canonical for suggestion in suggestions] == ["blue"]
    assert suggestions[0].score > 0.0


def test_normalize_runtime_field_prefers_override_and_lexicon_metadata() -> None:
    context = _build_context()

    override_result = normalize_runtime_field(
        field="category",
        value="tops alt",
        context=context,
        normalize=_norm,
        suggest_threshold=0.1,
        fuzzy_threshold=0.9,
    )
    lexicon_result = normalize_runtime_field(
        field="color_primary",
        value="marine",
        context=context,
        normalize=_norm,
        suggest_threshold=0.1,
        fuzzy_threshold=0.9,
    )

    assert override_result.matched_by == "override"
    assert override_result.canonical == "cat_tops"
    assert lexicon_result.matched_by == "lexicon"
    assert lexicon_result.canonical == "blue"
    assert lexicon_result.meta == {"family": "blue", "label": "Marine"}


def test_normalize_runtime_field_uses_fuzzy_then_legacy_then_root_suggestions() -> None:
    context = _build_context()

    fuzzy_result = normalize_runtime_field(
        field="material_main",
        value="coton",
        context=context,
        normalize=_norm,
        suggest_threshold=0.1,
        fuzzy_threshold=0.8,
    )
    legacy_result = normalize_runtime_field(
        field="category",
        value="historic_bucket",
        context=context,
        normalize=_norm,
        suggest_threshold=0.95,
        fuzzy_threshold=0.95,
    )
    none_result = normalize_runtime_field(
        field="category",
        value="mystery bucket",
        context=context,
        normalize=_norm,
        suggest_threshold=0.95,
        fuzzy_threshold=0.95,
    )

    assert fuzzy_result.matched_by == "fuzzy"
    assert fuzzy_result.canonical == "mat_cotton"
    assert legacy_result.matched_by == "legacy"
    assert legacy_result.canonical == "historic_bucket"
    assert none_result.matched_by == "none"
    assert [suggestion.canonical for suggestion in none_result.suggestions] == ["cat_tops", "cat_outerwear"]


def test_root_category_suggestions_respects_limit_and_labels() -> None:
    suggestions = root_category_suggestions(
        category_roots=["cat_tops", "cat_outerwear", "cat_dresses"],
        cat_label={"cat_tops": "Oberteile", "cat_outerwear": "Jacken", "cat_dresses": "Kleider"},
        limit=2,
    )

    assert [(suggestion.canonical, suggestion.label) for suggestion in suggestions] == [
        ("cat_tops", "Oberteile"),
        ("cat_outerwear", "Jacken"),
    ]

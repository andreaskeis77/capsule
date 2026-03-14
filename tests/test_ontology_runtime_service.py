from __future__ import annotations

from src.ontology_runtime import _norm
from src.ontology_runtime_service import (
    RuntimeNormalizationPolicy,
    RuntimeNormalizationState,
    decision_to_result,
    validate_or_normalize_value,
)
from src.ontology_runtime_matcher import MatchSuggestion, RuntimeNormalizationDecision
from src.ontology_runtime_types import empty_normalization_result


def _build_state() -> RuntimeNormalizationState:
    return RuntimeNormalizationState(
        idx_category={_norm("Oberteile"): "cat_tops", _norm("Jacken"): "cat_outerwear"},
        cat_label={"cat_tops": "Oberteile", "cat_outerwear": "Jacken"},
        idx_color={_norm("blue"): "blue", _norm("marine"): "blue"},
        idx_fit={_norm("regular"): "regular"},
        idx_collar={_norm("round_neck"): "round_neck"},
        idx_material={_norm("cotton"): "mat_cotton"},
        mat_label={"mat_cotton": "Baumwolle"},
        override={"category": {_norm("tops alt"): "cat_tops"}},
        color_lexicon={_norm("marine"): {"family": "blue", "label": "Marine"}},
        legacy={"category": ["historic_bucket"]},
        category_roots=["cat_tops", "cat_outerwear"],
    )


def test_decision_to_result_maps_matcher_suggestions_to_public_types() -> None:
    result = decision_to_result(
        RuntimeNormalizationDecision(
            field="category",
            original="oberteyle",
            canonical="cat_tops",
            matched_by="fuzzy",
            confidence=0.91,
            suggestions=[MatchSuggestion(canonical="cat_tops", score=0.91, label="Oberteile")],
            meta={"source": "test"},
        )
    )

    assert result.canonical == "cat_tops"
    assert result.matched_by == "fuzzy"
    assert result.suggestions[0].canonical == "cat_tops"
    assert result.suggestions[0].label == "Oberteile"
    assert result.meta == {"source": "test"}


def test_validate_or_normalize_value_respects_mode_off_and_strict_legacy() -> None:
    state = _build_state()

    canonical_off, result_off = validate_or_normalize_value(
        field="category",
        value="mystery bucket",
        state=state,
        policy=RuntimeNormalizationPolicy(
            suggest_threshold=0.95,
            fuzzy_threshold=0.95,
            mode="off",
            allow_legacy=False,
        ),
        normalize=_norm,
    )
    canonical_strict, result_strict = validate_or_normalize_value(
        field="category",
        value="historic_bucket",
        state=state,
        policy=RuntimeNormalizationPolicy(
            suggest_threshold=0.95,
            fuzzy_threshold=0.95,
            mode="strict",
            allow_legacy=False,
        ),
        normalize=_norm,
    )

    assert canonical_off == "mystery bucket"
    assert result_off.canonical is None
    assert [suggestion.canonical for suggestion in result_off.suggestions] == ["cat_tops", "cat_outerwear"]
    assert canonical_strict is None
    assert result_strict.matched_by == "legacy"


def test_empty_normalization_result_returns_none_match() -> None:
    result = empty_normalization_result(field="category")

    assert result.field == "category"
    assert result.canonical is None
    assert result.matched_by == "none"
    assert result.suggestions == []

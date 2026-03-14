from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.ontology_runtime_matcher import (
    RuntimeMatchContext,
    RuntimeNormalizationDecision,
    normalize_runtime_field,
)
from src.ontology_runtime_types import (
    NormalizationResult,
    Suggestion,
    empty_normalization_result,
)

NormalizeFn = Callable[[str], str]


@dataclass(frozen=True)
class RuntimeNormalizationState:
    idx_category: Dict[str, str]
    cat_label: Dict[str, str]
    idx_color: Dict[str, str]
    idx_fit: Dict[str, str]
    idx_collar: Dict[str, str]
    idx_material: Dict[str, str]
    mat_label: Dict[str, str]
    override: Dict[str, Dict[str, str]]
    color_lexicon: Dict[str, Dict[str, Any]]
    legacy: Dict[str, List[str]]
    category_roots: List[str]


@dataclass(frozen=True)
class RuntimeNormalizationPolicy:
    suggest_threshold: float
    fuzzy_threshold: float
    mode: str
    allow_legacy: bool


def build_match_context(state: RuntimeNormalizationState) -> RuntimeMatchContext:
    return RuntimeMatchContext(
        idx_category=state.idx_category,
        cat_label=state.cat_label,
        idx_color=state.idx_color,
        idx_fit=state.idx_fit,
        idx_collar=state.idx_collar,
        idx_material=state.idx_material,
        mat_label=state.mat_label,
        override=state.override,
        color_lexicon=state.color_lexicon,
        legacy=state.legacy,
        category_roots=state.category_roots,
    )


def decision_to_result(decision: RuntimeNormalizationDecision) -> NormalizationResult:
    return NormalizationResult(
        field=decision.field,
        original=decision.original,
        canonical=decision.canonical,
        matched_by=decision.matched_by,
        confidence=decision.confidence,
        suggestions=[
            Suggestion(
                canonical=suggestion.canonical,
                score=suggestion.score,
                label=suggestion.label,
            )
            for suggestion in decision.suggestions
        ],
        meta=decision.meta,
    )


def normalize_value(
    *,
    field: str,
    value: str,
    state: RuntimeNormalizationState,
    policy: RuntimeNormalizationPolicy,
    normalize: NormalizeFn,
) -> NormalizationResult:
    decision = normalize_runtime_field(
        field=field,
        value=value,
        context=build_match_context(state),
        normalize=normalize,
        suggest_threshold=policy.suggest_threshold,
        fuzzy_threshold=policy.fuzzy_threshold,
    )
    return decision_to_result(decision)


def validate_or_normalize_value(
    *,
    field: str,
    value: Optional[str],
    state: RuntimeNormalizationState,
    policy: RuntimeNormalizationPolicy,
    normalize: NormalizeFn,
) -> Tuple[Optional[str], NormalizationResult]:
    if value is None:
        return None, empty_normalization_result(field=field)

    result = normalize_value(
        field=field,
        value=value,
        state=state,
        policy=policy,
        normalize=normalize,
    )

    if policy.mode == "off":
        return value, result

    if result.canonical is None:
        return None, result

    if policy.mode == "strict" and result.matched_by == "legacy" and not policy.allow_legacy:
        return None, result

    return result.canonical, result

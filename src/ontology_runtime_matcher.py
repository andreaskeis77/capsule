from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

NormalizeFn = Callable[[str], str]

SUPPORTED_FIELDS = (
    "category",
    "color_primary",
    "fit",
    "collar",
    "material_main",
)


@dataclass(frozen=True)
class MatchSuggestion:
    canonical: str
    score: float
    label: Optional[str] = None


@dataclass(frozen=True)
class RuntimeNormalizationDecision:
    field: str
    original: str
    canonical: Optional[str]
    matched_by: str
    confidence: float
    suggestions: List[MatchSuggestion]
    meta: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class RuntimeMatchContext:
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


def suggest_matches(
    *,
    index: Dict[str, str],
    label_map: Optional[Dict[str, str]],
    value: str,
    normalize: NormalizeFn,
    suggest_threshold: float,
    limit: int = 5,
) -> List[MatchSuggestion]:
    query = normalize(value)
    if not query:
        return []

    scored: Dict[str, float] = {}
    close_matches = difflib.get_close_matches(
        query,
        list(index.keys()),
        n=50,
        cutoff=suggest_threshold,
    )
    for key in close_matches:
        canonical_value = index[key]
        score = difflib.SequenceMatcher(None, query, key).ratio()
        scored[canonical_value] = max(scored.get(canonical_value, 0.0), score)

    ranked = sorted(scored.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [
        MatchSuggestion(
            canonical=canonical_value,
            score=round(score, 3),
            label=(label_map or {}).get(canonical_value),
        )
        for canonical_value, score in ranked
    ]


def root_category_suggestions(
    *,
    category_roots: List[str],
    cat_label: Dict[str, str],
    limit: int = 5,
) -> List[MatchSuggestion]:
    return [
        MatchSuggestion(canonical=category_id, score=0.2, label=cat_label.get(category_id))
        for category_id in category_roots[:limit]
    ]


def index_for_field(
    *,
    field: str,
    context: RuntimeMatchContext,
) -> Tuple[Dict[str, str], Optional[Dict[str, str]]]:
    if field == "category":
        return context.idx_category, context.cat_label
    if field == "color_primary":
        return context.idx_color, None
    if field == "fit":
        return context.idx_fit, None
    if field == "collar":
        return context.idx_collar, None
    if field == "material_main":
        return context.idx_material, context.mat_label
    raise ValueError(f"Unsupported field: {field}")


def normalize_runtime_field(
    *,
    field: str,
    value: str,
    context: RuntimeMatchContext,
    normalize: NormalizeFn,
    suggest_threshold: float,
    fuzzy_threshold: float,
) -> RuntimeNormalizationDecision:
    original = value or ""
    stripped_value = original.strip()
    if not stripped_value:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=None,
            matched_by="none",
            confidence=0.0,
            suggestions=[],
            meta=None,
        )

    index, labels = index_for_field(field=field, context=context)
    normalized_key = normalize(stripped_value)
    suggestions = suggest_matches(
        index=index,
        label_map=labels,
        value=stripped_value,
        normalize=normalize,
        suggest_threshold=suggest_threshold,
        limit=5,
    )

    overrides = context.override.get(field, {})
    if normalized_key in overrides:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=overrides[normalized_key],
            matched_by="override",
            confidence=1.0,
            suggestions=suggestions,
            meta=None,
        )

    if field == "color_primary" and normalized_key in context.color_lexicon:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=context.idx_color.get(normalized_key),
            matched_by="lexicon",
            confidence=1.0,
            suggestions=suggestions,
            meta=dict(context.color_lexicon[normalized_key]),
        )

    canonical_exact = index.get(normalized_key)
    if canonical_exact:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=canonical_exact,
            matched_by="exact/synonym",
            confidence=1.0,
            suggestions=suggestions,
            meta=None,
        )

    if suggestions:
        best = suggestions[0]
        if best.score >= fuzzy_threshold:
            return RuntimeNormalizationDecision(
                field=field,
                original=original,
                canonical=best.canonical,
                matched_by="fuzzy",
                confidence=best.score,
                suggestions=suggestions,
                meta=None,
            )

    legacy_values = set(context.legacy.get(field, []) or [])
    if stripped_value in legacy_values:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=stripped_value,
            matched_by="legacy",
            confidence=1.0,
            suggestions=suggestions,
            meta=None,
        )

    if field == "category" and not suggestions and context.category_roots:
        return RuntimeNormalizationDecision(
            field=field,
            original=original,
            canonical=None,
            matched_by="none",
            confidence=0.0,
            suggestions=root_category_suggestions(
                category_roots=context.category_roots,
                cat_label=context.cat_label,
                limit=5,
            ),
            meta=None,
        )

    return RuntimeNormalizationDecision(
        field=field,
        original=original,
        canonical=None,
        matched_by="none",
        confidence=0.0,
        suggestions=suggestions,
        meta=None,
    )

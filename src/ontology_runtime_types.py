from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Suggestion:
    canonical: str
    score: float
    label: Optional[str] = None


@dataclass(frozen=True)
class NormalizationResult:
    field: str
    original: str
    canonical: Optional[str]
    matched_by: str  # override|lexicon|exact/synonym|fuzzy|legacy|none
    confidence: float
    suggestions: List[Suggestion]
    meta: Optional[Dict[str, Any]] = None


def empty_normalization_result(
    *,
    field: str,
    original: str = "",
) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        canonical=None,
        matched_by="none",
        confidence=0.0,
        suggestions=[],
        meta=None,
    )

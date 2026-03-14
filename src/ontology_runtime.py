# FILE: src/ontology_runtime.py
from __future__ import annotations

import difflib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src import settings
from src.ontology_runtime_index import build_runtime_indexes
from src.ontology_runtime_loader import build_runtime_seed_data, extract_yaml_from_md
from src.ontology_runtime_sources import load_color_lexicon, load_legacy_values, load_overrides

logger = logging.getLogger("WardrobeControl")


def _extract_yaml_from_md(path: Path) -> str:
    return extract_yaml_from_md(path)


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    if not s:
        return ""
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[\(\)\[\]\{\},;:\/\\\|]+", " ", s)
    s = s.replace("&", " and ")
    s = re.sub(r"[\s\-]+", " ", s).strip()
    s = re.sub(r"[^a-z0-9_ ]+", "", s)
    return s


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


class OntologyManager:
    def __init__(
        self,
        categories: List[Dict[str, Any]],
        value_sets: Dict[str, List[Dict[str, Any]]],
        materials: List[Dict[str, Any]],
        *,
        legacy: Optional[Dict[str, List[str]]] = None,
        overrides: Optional[Dict[str, Dict[str, str]]] = None,
        color_lexicon: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.categories = categories
        self.value_sets = value_sets
        self.materials = materials
        self.legacy = legacy or {}
        self.overrides_raw = overrides or {}
        self.color_lexicon_raw = color_lexicon or {}

        self._idx_category: Dict[str, str] = {}
        self._cat_label: Dict[str, str] = {}
        self._cat_parent: Dict[str, Optional[str]] = {}

        self._idx_color: Dict[str, str] = {}
        self._idx_fit: Dict[str, str] = {}
        self._idx_collar: Dict[str, str] = {}
        self._idx_material: Dict[str, str] = {}
        self._mat_label: Dict[str, str] = {}

        self._override: Dict[str, Dict[str, str]] = {
            "category": {},
            "color_primary": {},
            "fit": {},
            "collar": {},
            "material_main": {},
        }

        self._color_lexicon: Dict[str, Dict[str, Any]] = {}
        self._category_roots: List[str] = []

        self._build_indexes()

    @classmethod
    def load_from_files(cls) -> "OntologyManager":
        seed_data = build_runtime_seed_data(settings.ONTOLOGY_DIR)

        legacy = cls._load_legacy_from_db()
        overrides = cls._load_overrides()
        color_lexicon = cls._load_color_lexicon()

        return cls(
            categories=seed_data["categories"],
            value_sets=seed_data["value_sets"],
            materials=seed_data["materials"],
            legacy=legacy,
            overrides=overrides,
            color_lexicon=color_lexicon,
        )

    @staticmethod
    def _load_overrides() -> Dict[str, Dict[str, str]]:
        return load_overrides(settings.ONTOLOGY_OVERRIDES_FILE)

    @staticmethod
    def _load_color_lexicon() -> Dict[str, Dict[str, Any]]:
        return load_color_lexicon(settings.ONTOLOGY_COLOR_LEXICON_FILE)

    @staticmethod
    def _load_legacy_from_db() -> Dict[str, List[str]]:
        return load_legacy_values(settings.DB_PATH)

    def _build_indexes(self) -> None:
        indexes = build_runtime_indexes(
            categories=self.categories,
            value_sets=self.value_sets,
            materials=self.materials,
            overrides_raw=self.overrides_raw,
            color_lexicon_raw=self.color_lexicon_raw,
            normalize=_norm,
            logger_instance=logger,
        )

        self._idx_category = indexes.idx_category
        self._cat_label = indexes.cat_label
        self._cat_parent = indexes.cat_parent
        self._idx_color = indexes.idx_color
        self._idx_fit = indexes.idx_fit
        self._idx_collar = indexes.idx_collar
        self._idx_material = indexes.idx_material
        self._mat_label = indexes.mat_label
        self._override = indexes.override
        self._color_lexicon = indexes.color_lexicon
        self._category_roots = indexes.category_roots

    def _suggest(
        self,
        index: Dict[str, str],
        label_map: Optional[Dict[str, str]],
        value: str,
        limit: int = 5,
    ) -> List[Suggestion]:
        query = _norm(value)
        if not query:
            return []

        candidate_keys = list(index.keys())
        scored: Dict[str, float] = {}

        close_matches = difflib.get_close_matches(
            query,
            candidate_keys,
            n=50,
            cutoff=settings.ONTOLOGY_SUGGEST_THRESHOLD,
        )
        for key in close_matches:
            canonical_value = index[key]
            score = difflib.SequenceMatcher(None, query, key).ratio()
            scored[canonical_value] = max(scored.get(canonical_value, 0.0), score)

        ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:limit]
        suggestions: List[Suggestion] = []
        for canonical_value, score in ranked:
            label = (label_map or {}).get(canonical_value)
            suggestions.append(
                Suggestion(canonical=canonical_value, score=round(score, 3), label=label)
            )
        return suggestions

    def _index_for(self, field: str) -> Tuple[Dict[str, str], Optional[Dict[str, str]]]:
        if field == "category":
            return self._idx_category, self._cat_label
        if field == "color_primary":
            return self._idx_color, None
        if field == "fit":
            return self._idx_fit, None
        if field == "collar":
            return self._idx_collar, None
        if field == "material_main":
            return self._idx_material, self._mat_label
        raise ValueError(f"Unsupported field: {field}")

    def normalize_field(self, field: str, value: str) -> NormalizationResult:
        original = value or ""
        stripped_value = original.strip()
        if not stripped_value:
            return NormalizationResult(
                field=field,
                original=original,
                canonical=None,
                matched_by="none",
                confidence=0.0,
                suggestions=[],
                meta=None,
            )

        index, labels = self._index_for(field)
        normalized_key = _norm(stripped_value)

        overrides = self._override.get(field, {})
        if normalized_key in overrides:
            canonical = overrides[normalized_key]
            suggestions = self._suggest(index, labels, stripped_value, limit=5)
            return NormalizationResult(
                field=field,
                original=original,
                canonical=canonical,
                matched_by="override",
                confidence=1.0,
                suggestions=suggestions,
                meta=None,
            )

        if field == "color_primary" and normalized_key in self._color_lexicon:
            canonical = self._idx_color.get(normalized_key)
            suggestions = self._suggest(index, labels, stripped_value, limit=5)
            return NormalizationResult(
                field=field,
                original=original,
                canonical=canonical,
                matched_by="lexicon",
                confidence=1.0,
                suggestions=suggestions,
                meta=dict(self._color_lexicon[normalized_key]),
            )

        canonical_exact = index.get(normalized_key)
        if canonical_exact:
            suggestions = self._suggest(index, labels, stripped_value, limit=5)
            return NormalizationResult(
                field=field,
                original=original,
                canonical=canonical_exact,
                matched_by="exact/synonym",
                confidence=1.0,
                suggestions=suggestions,
                meta=None,
            )

        suggestions = self._suggest(index, labels, stripped_value, limit=5)
        if suggestions:
            best = suggestions[0]
            if best.score >= settings.ONTOLOGY_FUZZY_THRESHOLD:
                return NormalizationResult(
                    field=field,
                    original=original,
                    canonical=best.canonical,
                    matched_by="fuzzy",
                    confidence=best.score,
                    suggestions=suggestions,
                    meta=None,
                )

        legacy_values = set(self.legacy.get(field, []) or [])
        if stripped_value in legacy_values:
            return NormalizationResult(
                field=field,
                original=original,
                canonical=stripped_value,
                matched_by="legacy",
                confidence=1.0,
                suggestions=suggestions,
                meta=None,
            )

        if field == "category" and not suggestions and self._category_roots:
            root_suggestions = [
                Suggestion(canonical=category_id, score=0.2, label=self._cat_label.get(category_id))
                for category_id in self._category_roots[:5]
            ]
            return NormalizationResult(
                field=field,
                original=original,
                canonical=None,
                matched_by="none",
                confidence=0.0,
                suggestions=root_suggestions,
                meta=None,
            )

        return NormalizationResult(
            field=field,
            original=original,
            canonical=None,
            matched_by="none",
            confidence=0.0,
            suggestions=suggestions,
            meta=None,
        )

    def validate_or_normalize(self, field: str, value: Optional[str]) -> Tuple[Optional[str], NormalizationResult]:
        if value is None:
            nr = NormalizationResult(
                field=field,
                original="",
                canonical=None,
                matched_by="none",
                confidence=0.0,
                suggestions=[],
                meta=None,
            )
            return None, nr

        nr = self.normalize_field(field, value)

        if settings.ONTOLOGY_MODE == "off":
            return value, nr

        if nr.canonical is None:
            return None, nr

        if settings.ONTOLOGY_MODE == "strict":
            if nr.matched_by == "legacy" and not settings.ONTOLOGY_ALLOW_LEGACY:
                return None, nr

        return nr.canonical, nr

# FILE: src/ontology_runtime.py
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src import settings
from src.ontology_runtime_index import build_runtime_indexes
from src.ontology_runtime_loader import build_runtime_seed_data, extract_yaml_from_md
from src.ontology_runtime_service import (
    RuntimeNormalizationPolicy,
    RuntimeNormalizationState,
    normalize_value,
    validate_or_normalize_value,
)
from src.ontology_runtime_types import NormalizationResult, Suggestion
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

    def _normalization_state(self) -> RuntimeNormalizationState:
        return RuntimeNormalizationState(
            idx_category=self._idx_category,
            cat_label=self._cat_label,
            idx_color=self._idx_color,
            idx_fit=self._idx_fit,
            idx_collar=self._idx_collar,
            idx_material=self._idx_material,
            mat_label=self._mat_label,
            override=self._override,
            color_lexicon=self._color_lexicon,
            legacy=self.legacy,
            category_roots=self._category_roots,
        )

    @staticmethod
    def _normalization_policy() -> RuntimeNormalizationPolicy:
        return RuntimeNormalizationPolicy(
            suggest_threshold=settings.ONTOLOGY_SUGGEST_THRESHOLD,
            fuzzy_threshold=settings.ONTOLOGY_FUZZY_THRESHOLD,
            mode=settings.ONTOLOGY_MODE,
            allow_legacy=settings.ONTOLOGY_ALLOW_LEGACY,
        )

    def normalize_field(self, field: str, value: str) -> NormalizationResult:
        return normalize_value(
            field=field,
            value=value,
            state=self._normalization_state(),
            policy=self._normalization_policy(),
            normalize=_norm,
        )

    def validate_or_normalize(self, field: str, value: Optional[str]) -> Tuple[Optional[str], NormalizationResult]:
        return validate_or_normalize_value(
            field=field,
            value=value,
            state=self._normalization_state(),
            policy=self._normalization_policy(),
            normalize=_norm,
        )

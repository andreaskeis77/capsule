from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

NormalizeFn = Callable[[str], str]

SUPPORTED_OVERRIDE_FIELDS = (
    "category",
    "color_primary",
    "fit",
    "collar",
    "material_main",
)


@dataclass(frozen=True)
class RuntimeIndexes:
    idx_category: Dict[str, str]
    cat_label: Dict[str, str]
    cat_parent: Dict[str, Optional[str]]
    idx_color: Dict[str, str]
    idx_fit: Dict[str, str]
    idx_collar: Dict[str, str]
    idx_material: Dict[str, str]
    mat_label: Dict[str, str]
    override: Dict[str, Dict[str, str]]
    color_lexicon: Dict[str, Dict[str, Any]]
    category_roots: List[str]


@dataclass(frozen=True)
class CategoryIndexData:
    idx_category: Dict[str, str]
    cat_label: Dict[str, str]
    cat_parent: Dict[str, Optional[str]]
    cat_ids: Set[str]
    category_roots: List[str]


@dataclass(frozen=True)
class ValueIndexData:
    index: Dict[str, str]
    canonical_values: Set[str]


@dataclass(frozen=True)
class MaterialIndexData:
    idx_material: Dict[str, str]
    mat_label: Dict[str, str]
    material_ids: Set[str]


@dataclass(frozen=True)
class OverrideTarget:
    canonical_values: Set[str]
    index: Dict[str, str]


def build_category_indexes(
    categories: Sequence[Dict[str, Any]],
    *,
    normalize: NormalizeFn,
) -> CategoryIndexData:
    idx_category: Dict[str, str] = {}
    cat_label: Dict[str, str] = {}
    cat_parent: Dict[str, Optional[str]] = {}
    cat_ids: Set[str] = set()

    for category in categories:
        category_id = category.get("id", "")
        if not category_id:
            continue

        cat_ids.add(category_id)
        parent_id = category.get("parent_id") or None
        cat_parent[category_id] = parent_id

        label_de = category.get("label_de") or ""
        label_en = category.get("label_en") or ""
        cat_label[category_id] = label_de or label_en or category_id

        tokens: List[str] = [category_id, label_de, label_en]
        examples = category.get("examples") or []
        if isinstance(examples, list):
            tokens.extend(str(example) for example in examples)

        for token in tokens:
            normalized_token = normalize(str(token))
            if normalized_token:
                idx_category[normalized_token] = category_id

    category_roots = [category_id for category_id, parent_id in cat_parent.items() if not parent_id]
    return CategoryIndexData(
        idx_category=idx_category,
        cat_label=cat_label,
        cat_parent=cat_parent,
        cat_ids=cat_ids,
        category_roots=category_roots,
    )


def build_value_index(
    rows: Sequence[Dict[str, Any]],
    *,
    normalize: NormalizeFn,
) -> ValueIndexData:
    index: Dict[str, str] = {}
    canonical_values: Set[str] = set()

    for row in rows:
        value = row.get("value")
        if not value:
            continue

        canonical_values.add(value)
        index[normalize(str(value))] = value
        for synonym in row.get("synonyms_de") or []:
            index[normalize(str(synonym))] = value

    return ValueIndexData(index=index, canonical_values=canonical_values)


def build_material_indexes(
    materials: Sequence[Dict[str, Any]],
    *,
    normalize: NormalizeFn,
) -> MaterialIndexData:
    idx_material: Dict[str, str] = {}
    mat_label: Dict[str, str] = {}
    material_ids: Set[str] = set()

    for material in materials:
        material_id = material.get("id")
        if not material_id:
            continue

        material_ids.add(material_id)
        label_de = material.get("label_de") or ""
        label_en = material.get("label_en") or ""
        mat_label[material_id] = label_de or label_en or material_id

        tokens: List[str] = [material_id, label_de, label_en]
        synonyms = material.get("synonyms") or []
        if isinstance(synonyms, list):
            tokens.extend(str(synonym) for synonym in synonyms)

        for token in tokens:
            normalized_token = normalize(str(token))
            if normalized_token:
                idx_material[normalized_token] = material_id

    return MaterialIndexData(
        idx_material=idx_material,
        mat_label=mat_label,
        material_ids=material_ids,
    )


__all__ = [
    "CategoryIndexData",
    "MaterialIndexData",
    "NormalizeFn",
    "OverrideTarget",
    "RuntimeIndexes",
    "SUPPORTED_OVERRIDE_FIELDS",
    "ValueIndexData",
    "build_category_indexes",
    "build_material_indexes",
    "build_value_index",
]

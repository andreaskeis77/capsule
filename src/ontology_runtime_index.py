from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

logger = logging.getLogger("WardrobeControl")

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


def empty_override_index() -> Dict[str, Dict[str, str]]:
    return {field: {} for field in SUPPORTED_OVERRIDE_FIELDS}


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


def override_targets(
    *,
    category_data: CategoryIndexData,
    color_data: ValueIndexData,
    fit_data: ValueIndexData,
    collar_data: ValueIndexData,
    material_data: MaterialIndexData,
) -> Dict[str, OverrideTarget]:
    return {
        "category": OverrideTarget(
            canonical_values=category_data.cat_ids,
            index=category_data.idx_category,
        ),
        "color_primary": OverrideTarget(
            canonical_values=color_data.canonical_values,
            index=color_data.index,
        ),
        "fit": OverrideTarget(
            canonical_values=fit_data.canonical_values,
            index=fit_data.index,
        ),
        "collar": OverrideTarget(
            canonical_values=collar_data.canonical_values,
            index=collar_data.index,
        ),
        "material_main": OverrideTarget(
            canonical_values=material_data.material_ids,
            index=material_data.idx_material,
        ),
    }


def apply_runtime_overrides(
    overrides_raw: Optional[Dict[str, Dict[str, str]]],
    *,
    targets: Dict[str, OverrideTarget],
    normalize: NormalizeFn,
    logger_instance: logging.Logger = logger,
) -> Dict[str, Dict[str, str]]:
    override_index = empty_override_index()

    for field, mapping in (overrides_raw or {}).items():
        if field not in override_index or not isinstance(mapping, dict):
            continue

        target = targets[field]
        for key, canonical_value_raw in mapping.items():
            normalized_key = normalize(str(key))
            canonical_value = str(canonical_value_raw).strip()
            if not normalized_key or not canonical_value:
                continue

            if canonical_value in target.canonical_values:
                target.index[normalized_key] = canonical_value
                override_index[field][normalized_key] = canonical_value
            else:
                logger_instance.warning(
                    f"Ignoring invalid override: field={field} key={key} -> {canonical_value}",
                    extra={"request_id": "-"},
                )

    return override_index


def apply_color_lexicon_entries(
    color_lexicon_raw: Optional[Dict[str, Dict[str, Any]]],
    *,
    valid_families: Iterable[str],
    color_index: Dict[str, str],
    normalize: NormalizeFn,
    logger_instance: logging.Logger = logger,
) -> Dict[str, Dict[str, Any]]:
    valid_family_set = set(valid_families)
    color_lexicon: Dict[str, Dict[str, Any]] = {}

    for raw_key, meta in (color_lexicon_raw or {}).items():
        normalized_key = normalize(str(raw_key))
        if not normalized_key:
            continue

        if not isinstance(meta, dict):
            logger_instance.warning(
                f"Ignoring invalid color_lexicon entry: {raw_key} -> ",
                extra={"request_id": "-"},
            )
            continue

        family = str(meta.get("family", "")).strip()
        if family and family in valid_family_set:
            color_lexicon[normalized_key] = dict(meta)
            color_index[normalized_key] = family
        else:
            logger_instance.warning(
                f"Ignoring invalid color_lexicon entry: {raw_key} -> {family}",
                extra={"request_id": "-"},
            )

    return color_lexicon


def build_runtime_indexes(
    *,
    categories: Sequence[Dict[str, Any]],
    value_sets: Dict[str, List[Dict[str, Any]]],
    materials: Sequence[Dict[str, Any]],
    overrides_raw: Optional[Dict[str, Dict[str, str]]],
    color_lexicon_raw: Optional[Dict[str, Dict[str, Any]]],
    normalize: NormalizeFn,
    logger_instance: logging.Logger = logger,
) -> RuntimeIndexes:
    category_data = build_category_indexes(categories, normalize=normalize)
    color_data = build_value_index(value_sets.get("color_primary", []), normalize=normalize)
    fit_data = build_value_index(value_sets.get("fit", []), normalize=normalize)
    collar_data = build_value_index(value_sets.get("collar", []), normalize=normalize)
    material_data = build_material_indexes(materials, normalize=normalize)

    targets = override_targets(
        category_data=category_data,
        color_data=color_data,
        fit_data=fit_data,
        collar_data=collar_data,
        material_data=material_data,
    )
    override_index = apply_runtime_overrides(
        overrides_raw,
        targets=targets,
        normalize=normalize,
        logger_instance=logger_instance,
    )
    color_lexicon = apply_color_lexicon_entries(
        color_lexicon_raw,
        valid_families=color_data.canonical_values,
        color_index=color_data.index,
        normalize=normalize,
        logger_instance=logger_instance,
    )

    return RuntimeIndexes(
        idx_category=category_data.idx_category,
        cat_label=category_data.cat_label,
        cat_parent=category_data.cat_parent,
        idx_color=color_data.index,
        idx_fit=fit_data.index,
        idx_collar=collar_data.index,
        idx_material=material_data.idx_material,
        mat_label=material_data.mat_label,
        override=override_index,
        color_lexicon=color_lexicon,
        category_roots=category_data.category_roots,
    )

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

from src.ontology_runtime_index_builders import (
    CategoryIndexData,
    MaterialIndexData,
    NormalizeFn,
    OverrideTarget,
    SUPPORTED_OVERRIDE_FIELDS,
    ValueIndexData,
)

logger = logging.getLogger("WardrobeControl")


def empty_override_index() -> Dict[str, Dict[str, str]]:
    return {field: {} for field in SUPPORTED_OVERRIDE_FIELDS}


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


__all__ = [
    "apply_color_lexicon_entries",
    "apply_runtime_overrides",
    "empty_override_index",
    "override_targets",
]

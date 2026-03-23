from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence

from src.ontology_runtime_index_builders import (
    CategoryIndexData,
    MaterialIndexData,
    NormalizeFn,
    OverrideTarget,
    RuntimeIndexes,
    SUPPORTED_OVERRIDE_FIELDS,
    ValueIndexData,
    build_category_indexes,
    build_material_indexes,
    build_value_index,
)
from src.ontology_runtime_index_customization import (
    apply_color_lexicon_entries,
    apply_runtime_overrides,
    empty_override_index,
    override_targets,
)

logger = logging.getLogger("WardrobeControl")


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


__all__ = [
    "CategoryIndexData",
    "MaterialIndexData",
    "NormalizeFn",
    "OverrideTarget",
    "RuntimeIndexes",
    "SUPPORTED_OVERRIDE_FIELDS",
    "ValueIndexData",
    "apply_color_lexicon_entries",
    "apply_runtime_overrides",
    "build_category_indexes",
    "build_material_indexes",
    "build_runtime_indexes",
    "build_value_index",
    "empty_override_index",
    "override_targets",
]

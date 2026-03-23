from __future__ import annotations

from typing import Dict, List

from src.category_map_registry import (
    ADMIN_ALL_KEYS,
    ADMIN_GROUPS,
    ADMIN_LABEL,
    CATEGORY_SPEC_BY_KEY,
    CATEGORY_SPECS,
    CategorySpec,
    FILTER_ALL_KEYS,
    FILTER_GROUPS,
    FILTER_LABEL,
    FILTER_MATCH,
    GROUP_ACCESSORIES,
    GROUP_APPAREL,
    GROUP_JEWELRY,
    GROUP_ORDER,
    KEY_TO_GROUP,
    LEGACY_TOP_LABEL_TO_FILTER_KEY,
    QUICK_FILTER_ORDER,
)
from src.category_map_rules import (
    _contains_any,
    _fold_de,
    _words_blob,
    category_group_for_internal,
    display_category_label,
    infer_internal_category,
    normalize_filter_key,
)


def admin_option_groups() -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for group in GROUP_ORDER:
        keys = ADMIN_GROUPS.get(group, [])
        options = [{"value": key, "label": ADMIN_LABEL[key]} for key in keys if key in ADMIN_LABEL]
        out.append({"label": group, "options": options})
    return out


__all__ = [
    "ADMIN_ALL_KEYS",
    "ADMIN_GROUPS",
    "ADMIN_LABEL",
    "CATEGORY_SPEC_BY_KEY",
    "CATEGORY_SPECS",
    "CategorySpec",
    "FILTER_ALL_KEYS",
    "FILTER_GROUPS",
    "FILTER_LABEL",
    "FILTER_MATCH",
    "GROUP_ACCESSORIES",
    "GROUP_APPAREL",
    "GROUP_JEWELRY",
    "GROUP_ORDER",
    "KEY_TO_GROUP",
    "LEGACY_TOP_LABEL_TO_FILTER_KEY",
    "QUICK_FILTER_ORDER",
    "_contains_any",
    "_fold_de",
    "_words_blob",
    "admin_option_groups",
    "category_group_for_internal",
    "display_category_label",
    "infer_internal_category",
    "normalize_filter_key",
]

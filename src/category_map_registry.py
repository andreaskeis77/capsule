from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Set, Tuple

# -----------------------------
# Groups (for UI dropdown optgroups)
# -----------------------------
GROUP_APPAREL = "Bekleidung"
GROUP_JEWELRY = "Schmuck"
GROUP_ACCESSORIES = "Accessoires"
GROUP_ORDER: List[str] = [GROUP_APPAREL, GROUP_JEWELRY, GROUP_ACCESSORIES]


@dataclass(frozen=True)
class CategorySpec:
    """Canonical metadata for one category key.

    This registry is the single source of truth for labels, groups and
    UI visibility. Public facades can import and re-export the derived
    structures so external imports stay stable.
    """

    key: str
    label: str
    group: str
    in_admin: bool = True
    in_filter: bool = True
    quick_filter: bool = False
    filter_matches: FrozenSet[str] = frozenset()


CATEGORY_SPECS: Tuple[CategorySpec, ...] = (
    # Bekleidung
    CategorySpec("cat_dresses", "Kleider", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_blouses", "Blusen", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_belts", "Gürtel", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_sweaters", "Pullover", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_tshirts", "T-Shirts", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_blazers", "Blazer", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_tops", "Oberteile", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_skirts", "Röcke", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_trousers", "Hosen", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_tights", "Strumpfhosen", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_cardigans", "Strickjacken", GROUP_APPAREL, quick_filter=True),
    CategorySpec("cat_jackets", "Jacken", GROUP_APPAREL, in_filter=False),
    CategorySpec("cat_coats", "Mäntel", GROUP_APPAREL, in_filter=False),
    CategorySpec(
        "cat_outerwear",
        "Jacken / Mäntel",
        GROUP_APPAREL,
        in_admin=False,
        filter_matches=frozenset({"cat_jackets", "cat_coats"}),
        quick_filter=True,
    ),
    CategorySpec("cat_other", "Anderes", GROUP_APPAREL),
    # Schmuck
    CategorySpec("cat_earrings", "Ohrringe", GROUP_JEWELRY),
    CategorySpec("cat_watches", "Uhren", GROUP_JEWELRY),
    CategorySpec("cat_rings", "Ringe", GROUP_JEWELRY),
    CategorySpec("cat_necklaces", "Ketten", GROUP_JEWELRY),
    CategorySpec("cat_brooches", "Broschen", GROUP_JEWELRY),
    # Accessoires
    CategorySpec("cat_hats", "Haare / Mützen", GROUP_ACCESSORIES),
    CategorySpec("cat_bags", "Taschen", GROUP_ACCESSORIES),
    CategorySpec("cat_shoes", "Schuhe", GROUP_ACCESSORIES),
)

CATEGORY_SPEC_BY_KEY: Dict[str, CategorySpec] = {spec.key: spec for spec in CATEGORY_SPECS}

# -----------------------------
# Canonical INTERNAL category keys (stored in DB)
# -----------------------------
ADMIN_LABEL: Dict[str, str] = {
    spec.key: spec.label for spec in CATEGORY_SPECS if spec.in_admin
}
ADMIN_GROUPS: Dict[str, List[str]] = {
    group: [spec.key for spec in CATEGORY_SPECS if spec.in_admin and spec.group == group]
    for group in GROUP_ORDER
}
ADMIN_ALL_KEYS: Set[str] = set(ADMIN_LABEL.keys())
KEY_TO_GROUP: Dict[str, str] = {
    spec.key: spec.group for spec in CATEGORY_SPECS if spec.in_admin
}

# -----------------------------
# UI filter keys (NOT all are stored in DB)
# -----------------------------
FILTER_LABEL: Dict[str, str] = {
    spec.key: spec.label for spec in CATEGORY_SPECS if spec.in_filter
}
FILTER_GROUPS: Dict[str, List[str]] = {
    group: [spec.key for spec in CATEGORY_SPECS if spec.in_filter and spec.group == group]
    for group in GROUP_ORDER
}
FILTER_MATCH: Dict[str, Set[str]] = {
    spec.key: set(spec.filter_matches or {spec.key})
    for spec in CATEGORY_SPECS
    if spec.in_filter
}
FILTER_ALL_KEYS: Set[str] = set(FILTER_LABEL.keys())

# Quick chips: starred categories (+ outerwear group)
QUICK_FILTER_ORDER: List[str] = [
    spec.key for spec in CATEGORY_SPECS if spec.quick_filter and spec.in_filter
]

# Backward compat: old dashboard labels -> new filter keys
LEGACY_TOP_LABEL_TO_FILTER_KEY: Dict[str, str] = {
    "kleider": "cat_dresses",
    "blusen & oberteile": "cat_tops",
    "hosen": "cat_trousers",
    "roecke": "cat_skirts",
    "röcke": "cat_skirts",
    "jacken & mäntel": "cat_outerwear",
    "schuhe": "cat_shoes",
    "handtaschen": "cat_bags",
    "sonstiges": "cat_other",
    "anderes": "cat_other",
    "andere": "cat_other",
}


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
]

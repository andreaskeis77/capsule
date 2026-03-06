from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple

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
    UI visibility. The legacy public constants below are still exported so the
    rest of the application can keep its current imports unchanged.
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


def _fold_de(s: str) -> str:
    s = (s or "").strip().lower()
    return (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("Ã¤", "ae")
        .replace("Ã¶", "oe")
        .replace("Ã¼", "ue")
        .replace("ÃŸ", "ss")
    )


def _words_blob(s: str) -> str:
    folded = _fold_de(s)
    folded = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    return f" {folded} " if folded else " "


def normalize_filter_key(raw: Optional[str]) -> str:
    if not raw:
        return ""
    s = raw.strip()
    if not s:
        return ""
    if s in FILTER_ALL_KEYS:
        return s
    n = _fold_de(s)
    if n in LEGACY_TOP_LABEL_TO_FILTER_KEY:
        return LEGACY_TOP_LABEL_TO_FILTER_KEY[n]
    for key, label in FILTER_LABEL.items():
        if _fold_de(label) == n:
            return key
    return ""


def category_group_for_internal(internal_key: Optional[str]) -> str:
    if not internal_key:
        return ""
    return KEY_TO_GROUP.get(internal_key, "")


def _contains_any(blob: str, tokens: Iterable[str]) -> bool:
    return any(token in blob for token in tokens)


def infer_internal_category(raw_category: Optional[str], name: Optional[str] = None) -> Optional[str]:
    raw = (raw_category or "").strip()
    nm = (name or "").strip()
    if raw in ADMIN_ALL_KEYS:
        return raw

    raw_fold = _fold_de(raw)
    blob_raw = _fold_de(f"{raw} {nm}")
    blob_words = _words_blob(blob_raw)

    # explicit legacy bucket names (stored as category)
    if raw_fold in ("sonstiges", "anderes", "andere", "other"):
        return "cat_other"

    # guards: wrong-field-ish values should not be force-mapped
    if raw.startswith(("mat_", "fc_")):
        return None
    if raw and ("collar" in blob_raw or "neckline" in blob_raw):
        return None

    # --- Schmuck ---
    if ("ohrr" in blob_raw) or ("earring" in blob_raw):
        return "cat_earrings"
    if (" uhr " in blob_words) or ("watch" in blob_raw):
        return "cat_watches"
    if ("brosch" in blob_raw) or ("brooch" in blob_raw):
        return "cat_brooches"
    if ("kette" in blob_raw) or ("necklace" in blob_raw):
        return "cat_necklaces"
    if (" ring " in blob_words) or (" ringe " in blob_words) or ("rings" in blob_words):
        return "cat_rings"

    # --- Anderes (Poncho/Schal/Cape etc.) ---
    # IMPORTANT: must come before "cap"/hats heuristics to avoid substring issues
    # (cape contains cap).
    if _contains_any(
        blob_raw,
        [
            "poncho",
            "cape",
            "schal",
            "schaal",
            "tuch",
            "stola",
            "scarf",
            "shawl",
            "stole",
            "wrap",
            "pashmina",
        ],
    ):
        return "cat_other"

    # --- Schuhe / Taschen ---
    if _contains_any(
        blob_raw,
        ["schuh", "sneaker", "stiefel", "boot", "loafer", "pumps", "sandale", "sandal"],
    ):
        return "cat_shoes"
    if _contains_any(
        blob_raw,
        [
            "tasche",
            "handtasche",
            "clutch",
            "shopper",
            "rucksack",
            "backpack",
            "bag",
            "purse",
            "tote",
            "crossbody",
        ],
    ):
        return "cat_bags"

    # --- Haare / Mützen ---
    # Use word boundaries for short English tokens to avoid false positives
    # (e.g. "cape" contains "cap").
    if _contains_any(blob_raw, ["muetze", "mütze", "hut", "haarband", "haarreif"]):
        return "cat_hats"
    if any(word in blob_words for word in [" cap ", " hat ", " beanie "]):
        return "cat_hats"

    # --- Strumpfhosen ---
    if _contains_any(blob_raw, ["strumpfhose", "strumpf", "tights", "pantyhose", "denier"]):
        return "cat_tights"

    # --- Gürtel ---
    if _contains_any(blob_raw, ["guertel", "gürtel", " belt "]):
        return "cat_belts"

    # --- Kleider ---
    if _contains_any(blob_raw, ["kleid", "dress", "etuikleid", "midikleid", "maxikleid", "minikleid"]):
        return "cat_dresses"

    # --- Röcke ---
    if (" rock " in blob_words) or (" skirt " in blob_words) or ("skirt" in blob_raw):
        return "cat_skirts"

    # --- Hosen ---
    if _contains_any(
        blob_raw,
        ["hose", "pants", "trouser", "jeans", "leggings", "marlene", "culotte", "palazzo"],
    ):
        return "cat_trousers"

    # --- Blazer ---
    if _contains_any(blob_raw, ["blazer", "sakko"]):
        return "cat_blazers"

    # --- Strickjacken ---
    if _contains_any(blob_raw, ["strickjack", "cardigan", "longcardigan", "bolero"]):
        return "cat_cardigans"

    # --- Pullover ---
    if _contains_any(blob_raw, ["pullover", "sweater", "strickpullover", "rollkragen", "troyer"]):
        return "cat_sweaters"

    # --- Blusen ---
    if _contains_any(blob_raw, ["bluse", "blouse", "tunika", "hemdbluse", "schlupfbluse", "shirts_blouses"]):
        return "cat_blouses"
    if " hemd " in blob_words:
        return "cat_blouses"

    # --- T-Shirts ---
    if ("tshirt" in blob_raw) or (" t shirt " in blob_words) or (" t-shirt " in blob_words):
        return "cat_tshirts"
    if (" shirt " in blob_words) and ("bluse" not in blob_raw) and ("hemd" not in blob_raw):
        return "cat_tshirts"

    # --- Jacken / Mäntel (split) ---
    if _contains_any(blob_raw, ["mantel", "coat", "trench"]):
        return "cat_coats"
    if _contains_any(blob_raw, ["jacke", "jacket", "parka", "bomber"]):
        return "cat_jackets"

    # --- Oberteile ---
    if _contains_any(blob_raw, ["oberteil", "top", "tanktop", "camisole", "it_top_generic", "cat_apparel_tops", "cat_tops"]):
        return "cat_tops"
    if raw.startswith("cat_") and ("tops" in raw or "apparel_tops" in raw):
        return "cat_tops"

    return None


def display_category_label(raw_category: Optional[str], name: Optional[str] = None) -> str:
    internal = infer_internal_category(raw_category, name=name)
    if internal:
        return ADMIN_LABEL.get(internal, internal)
    raw = (raw_category or "").strip()
    if not raw:
        return "—"
    return f"⚠ unknown: {raw}"


def admin_option_groups() -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for group in GROUP_ORDER:
        keys = ADMIN_GROUPS.get(group, [])
        options = [{"value": key, "label": ADMIN_LABEL[key]} for key in keys if key in ADMIN_LABEL]
        out.append({"label": group, "options": options})
    return out

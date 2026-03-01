# FILE: src/category_map.py
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

# -----------------------------
# Groups (for UI dropdown optgroups)
# -----------------------------
GROUP_APPAREL = "Bekleidung"
GROUP_JEWELRY = "Schmuck"
GROUP_ACCESSORIES = "Accessoires"

GROUP_ORDER: List[str] = [GROUP_APPAREL, GROUP_JEWELRY, GROUP_ACCESSORIES]

# -----------------------------
# Canonical INTERNAL category keys (stored in DB)
# -----------------------------
ADMIN_LABEL: Dict[str, str] = {
    # Bekleidung
    "cat_dresses": "Kleider",
    "cat_blouses": "Blusen",
    "cat_belts": "Gürtel",
    "cat_sweaters": "Pullover",
    "cat_tshirts": "T-Shirts",
    "cat_blazers": "Blazer",
    "cat_tops": "Oberteile",
    "cat_skirts": "Röcke",
    "cat_trousers": "Hosen",
    "cat_tights": "Strumpfhosen",
    "cat_cardigans": "Strickjacken",
    "cat_jackets": "Jacken",
    "cat_coats": "Mäntel",
    "cat_other": "Anderes",
    # Schmuck
    "cat_earrings": "Ohrringe",
    "cat_watches": "Uhren",
    "cat_rings": "Ringe",
    "cat_necklaces": "Ketten",
    "cat_brooches": "Broschen",
    # Accessoires
    "cat_hats": "Haare / Mützen",
    "cat_bags": "Taschen",
    "cat_shoes": "Schuhe",
}

ADMIN_GROUPS: Dict[str, List[str]] = {
    GROUP_APPAREL: [
        "cat_dresses",
        "cat_blouses",
        "cat_tshirts",
        "cat_tops",
        "cat_sweaters",
        "cat_cardigans",
        "cat_blazers",
        "cat_skirts",
        "cat_trousers",
        "cat_tights",
        "cat_belts",
        "cat_jackets",
        "cat_coats",
        "cat_other",
    ],
    GROUP_JEWELRY: [
        "cat_earrings",
        "cat_watches",
        "cat_rings",
        "cat_necklaces",
        "cat_brooches",
    ],
    GROUP_ACCESSORIES: [
        "cat_hats",
        "cat_bags",
        "cat_shoes",
    ],
}

ADMIN_ALL_KEYS: Set[str] = set(ADMIN_LABEL.keys())

KEY_TO_GROUP: Dict[str, str] = {}
for g, keys in ADMIN_GROUPS.items():
    for k in keys:
        KEY_TO_GROUP[k] = g

# -----------------------------
# UI filter keys (NOT all are stored in DB)
# -----------------------------
FILTER_LABEL: Dict[str, str] = {
    # Bekleidung
    "cat_dresses": "Kleider",
    "cat_blouses": "Blusen",
    "cat_belts": "Gürtel",
    "cat_sweaters": "Pullover",
    "cat_tshirts": "T-Shirts",
    "cat_blazers": "Blazer",
    "cat_tops": "Oberteile",
    "cat_skirts": "Röcke",
    "cat_trousers": "Hosen",
    "cat_tights": "Strumpfhosen",
    "cat_cardigans": "Strickjacken",
    "cat_outerwear": "Jacken / Mäntel",  # UI-only (matches jackets+coats)
    "cat_other": "Anderes",
    # Schmuck
    "cat_earrings": "Ohrringe",
    "cat_watches": "Uhren",
    "cat_rings": "Ringe",
    "cat_necklaces": "Ketten",
    "cat_brooches": "Broschen",
    # Accessoires
    "cat_hats": "Haare / Mützen",
    "cat_bags": "Taschen",
    "cat_shoes": "Schuhe",
}

FILTER_GROUPS: Dict[str, List[str]] = {
    GROUP_APPAREL: [
        "cat_dresses",
        "cat_blouses",
        "cat_tshirts",
        "cat_tops",
        "cat_sweaters",
        "cat_cardigans",
        "cat_blazers",
        "cat_skirts",
        "cat_trousers",
        "cat_tights",
        "cat_belts",
        "cat_outerwear",
        "cat_other",
    ],
    GROUP_JEWELRY: [
        "cat_earrings",
        "cat_watches",
        "cat_rings",
        "cat_necklaces",
        "cat_brooches",
    ],
    GROUP_ACCESSORIES: [
        "cat_hats",
        "cat_bags",
        "cat_shoes",
    ],
}

FILTER_MATCH: Dict[str, Set[str]] = {
    **{k: {k} for k in ADMIN_ALL_KEYS},
    "cat_outerwear": {"cat_jackets", "cat_coats"},
}

FILTER_ALL_KEYS: Set[str] = set(FILTER_LABEL.keys())

# Quick chips: starred categories (+ outerwear group)
QUICK_FILTER_ORDER: List[str] = [
    "cat_dresses",
    "cat_blouses",
    "cat_belts",
    "cat_sweaters",
    "cat_tshirts",
    "cat_blazers",
    "cat_tops",
    "cat_skirts",
    "cat_trousers",
    "cat_tights",
    "cat_cardigans",
    "cat_outerwear",
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

    for k, lab in FILTER_LABEL.items():
        if _fold_de(lab) == n:
            return k

    return ""


def category_group_for_internal(internal_key: Optional[str]) -> str:
    if not internal_key:
        return ""
    return KEY_TO_GROUP.get(internal_key, "")


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
    # IMPORTANT: must come before "cap"/hats heuristics to avoid substring issues (cape contains cap).
    if any(
        t in blob_raw
        for t in ["poncho", "cape", "schal", "schaal", "tuch", "stola", "scarf", "shawl", "stole", "wrap", "pashmina"]
    ):
        return "cat_other"

    # --- Schuhe / Taschen ---
    if any(t in blob_raw for t in ["schuh", "sneaker", "stiefel", "boot", "loafer", "pumps", "sandale", "sandal"]):
        return "cat_shoes"
    if any(
        t in blob_raw
        for t in ["tasche", "handtasche", "clutch", "shopper", "rucksack", "backpack", "bag", "purse", "tote", "crossbody"]
    ):
        return "cat_bags"

    # --- Haare / Mützen ---
    # Use word-boundaries for short English tokens to avoid false positives (e.g. "cape" contains "cap").
    if any(t in blob_raw for t in ["muetze", "mütze", "hut", "haarband", "haarreif"]):
        return "cat_hats"
    if any(w in blob_words for w in [" cap ", " hat ", " beanie "]):
        return "cat_hats"

    # --- Strumpfhosen ---
    if any(t in blob_raw for t in ["strumpfhose", "strumpf", "tights", "pantyhose", "denier"]):
        return "cat_tights"

    # --- Gürtel ---
    if any(t in blob_raw for t in ["guertel", "gürtel", " belt "]):
        return "cat_belts"

    # --- Kleider ---
    if any(t in blob_raw for t in ["kleid", "dress", "etuikleid", "midikleid", "maxikleid", "minikleid"]):
        return "cat_dresses"

    # --- Röcke ---
    if (" rock " in blob_words) or (" skirt " in blob_words) or ("skirt" in blob_raw):
        return "cat_skirts"

    # --- Hosen ---
    if any(t in blob_raw for t in ["hose", "pants", "trouser", "jeans", "leggings", "marlene", "culotte", "palazzo"]):
        return "cat_trousers"

    # --- Blazer ---
    if any(t in blob_raw for t in ["blazer", "sakko"]):
        return "cat_blazers"

    # --- Strickjacken ---
    if any(t in blob_raw for t in ["strickjack", "cardigan", "longcardigan", "bolero"]):
        return "cat_cardigans"

    # --- Pullover ---
    if any(t in blob_raw for t in ["pullover", "sweater", "strickpullover", "rollkragen", "troyer"]):
        return "cat_sweaters"

    # --- Blusen ---
    if any(t in blob_raw for t in ["bluse", "blouse", "tunika", "hemdbluse", "schlupfbluse", "shirts_blouses"]):
        return "cat_blouses"
    if " hemd " in blob_words:
        return "cat_blouses"

    # --- T-Shirts ---
    if ("tshirt" in blob_raw) or (" t shirt " in blob_words) or (" t-shirt " in blob_words):
        return "cat_tshirts"
    if (" shirt " in blob_words) and ("bluse" not in blob_raw) and ("hemd" not in blob_raw):
        return "cat_tshirts"

    # --- Jacken / Mäntel (split) ---
    if any(t in blob_raw for t in ["mantel", "coat", "trench"]):
        return "cat_coats"
    if any(t in blob_raw for t in ["jacke", "jacket", "parka", "bomber"]):
        return "cat_jackets"

    # --- Oberteile ---
    if any(t in blob_raw for t in ["oberteil", "top", "tanktop", "camisole", "it_top_generic", "cat_apparel_tops", "cat_tops"]):
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
    for g in GROUP_ORDER:
        keys = ADMIN_GROUPS.get(g, [])
        options = [{"value": k, "label": ADMIN_LABEL[k]} for k in keys if k in ADMIN_LABEL]
        out.append({"label": g, "options": options})
    return out
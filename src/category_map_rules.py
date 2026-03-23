from __future__ import annotations

import re
from typing import Iterable, Optional

from src.category_map_registry import (
    ADMIN_ALL_KEYS,
    ADMIN_LABEL,
    FILTER_ALL_KEYS,
    FILTER_LABEL,
    KEY_TO_GROUP,
    LEGACY_TOP_LABEL_TO_FILTER_KEY,
)


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


def _contains_any(blob: str, tokens: Iterable[str]) -> bool:
    return any(token in blob for token in tokens)


def normalize_filter_key(raw: Optional[str]) -> str:
    if not raw:
        return ""
    s = raw.strip()
    if not s:
        return ""
    if s in FILTER_ALL_KEYS:
        return s
    n = _fold_de(s)
    for legacy_label, filter_key in LEGACY_TOP_LABEL_TO_FILTER_KEY.items():
        if _fold_de(legacy_label) == n:
            return filter_key
    for key, label in FILTER_LABEL.items():
        if _fold_de(label) == n:
            return key
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


__all__ = [
    "_contains_any",
    "_fold_de",
    "_words_blob",
    "category_group_for_internal",
    "display_category_label",
    "infer_internal_category",
    "normalize_filter_key",
]

from __future__ import annotations

from src import category_map as cm


def test_outerwear_filter_metadata_and_match_set():
    assert "cat_outerwear" in cm.FILTER_ALL_KEYS
    assert cm.FILTER_LABEL["cat_outerwear"] == "Jacken / Mäntel"
    assert cm.FILTER_MATCH["cat_outerwear"] == {"cat_jackets", "cat_coats"}
    assert "cat_outerwear" in cm.FILTER_GROUPS[cm.GROUP_APPAREL]


def test_normalize_filter_key_accepts_canonical_outerwear_key():
    assert cm.normalize_filter_key("cat_outerwear") == "cat_outerwear"
    assert cm.normalize_filter_key("") == ""
    assert cm.normalize_filter_key(None) == ""


def test_infer_internal_category_splits_jackets_and_coats():
    assert cm.infer_internal_category("jacke") == "cat_jackets"
    assert cm.infer_internal_category("mantel") == "cat_coats"

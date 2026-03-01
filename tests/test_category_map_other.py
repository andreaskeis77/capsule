# FILE: tests/test_category_map_other.py
from __future__ import annotations

from src import category_map as cm


def test_category_map_includes_cat_other():
    assert cm.ADMIN_LABEL["cat_other"] == "Anderes"
    assert cm.FILTER_LABEL["cat_other"] == "Anderes"
    assert "cat_other" in cm.ADMIN_ALL_KEYS
    assert "cat_other" in cm.FILTER_ALL_KEYS


def test_infer_maps_poncho_and_scarf_to_other():
    assert cm.infer_internal_category("poncho") == "cat_other"
    assert cm.infer_internal_category("cape") == "cat_other"
    assert cm.infer_internal_category("schal") == "cat_other"
    assert cm.infer_internal_category("stola") == "cat_other"
    assert cm.display_category_label("poncho") == "Anderes"
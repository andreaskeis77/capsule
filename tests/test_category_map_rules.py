from __future__ import annotations

from src import category_map as cm


def test_normalize_filter_key_supports_legacy_and_labels():
    assert cm.normalize_filter_key("Jacken & Mäntel") == "cat_outerwear"
    assert cm.normalize_filter_key("Taschen") == "cat_bags"


def test_infer_internal_category_keeps_cape_out_of_hat_false_positive():
    assert cm.infer_internal_category("Cape") == "cat_other"
    assert cm.infer_internal_category("Baseball Cap") == "cat_hats"


def test_display_category_label_known_and_unknown():
    assert cm.display_category_label("cat_blazers") == "Blazer"
    assert cm.display_category_label("mystery_bucket") == "⚠ unknown: mystery_bucket"

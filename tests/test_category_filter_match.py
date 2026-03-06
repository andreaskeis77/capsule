import src.category_map as cm


def _flat_filter_keys():
    groups = cm.FILTER_GROUPS

    if isinstance(groups, dict):
        for _group, keys in groups.items():
            for key in keys:
                yield key
        return

    for entry in groups:
        if isinstance(entry, tuple) and len(entry) == 2:
            _group, keys = entry
            for key in keys:
                yield key
        elif isinstance(entry, dict):
            options = entry.get("options", [])
            for opt in options:
                if isinstance(opt, dict) and "value" in opt:
                    yield opt["value"]
                elif isinstance(opt, str):
                    yield opt


def test_normalize_filter_key_supports_outerwear_key():
    assert cm.normalize_filter_key("cat_outerwear") == "cat_outerwear"



def test_filter_match_outerwear_matches_jackets_and_coats():
    assert cm.FILTER_MATCH["cat_outerwear"] == {"cat_jackets", "cat_coats"}



def test_filter_groups_include_outerwear_option():
    flat = list(_flat_filter_keys())
    assert "cat_outerwear" in flat



def test_quick_filter_order_includes_outerwear():
    assert "cat_outerwear" in cm.QUICK_FILTER_ORDER

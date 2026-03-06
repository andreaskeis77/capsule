from src.dashboard_category_view import (
    apply_base_filters,
    build_dashboard_category_view,
    build_filter_dropdown_groups,
    build_quick_filters,
    count_internal_categories,
    filter_items_by_category,
)


def _item(
    item_id: int,
    *,
    category_key: str | None,
    context: str = "private",
    needs_review: int = 0,
    name: str | None = None,
):
    return {
        "id": item_id,
        "name": name or f"item-{item_id}",
        "category_key": category_key,
        "context": context,
        "needs_review": needs_review,
    }



def test_apply_base_filters_respects_context_and_review_only():
    items_all = [
        _item(1, category_key="cat_blouses", context="business", needs_review=1),
        _item(2, category_key="cat_blouses", context="business", needs_review=0),
        _item(3, category_key="cat_jackets", context="private", needs_review=1),
    ]

    filtered = apply_base_filters(items_all, ctx="business", review_only=True)

    assert [it["id"] for it in filtered] == [1]



def test_build_dashboard_category_view_outerwear_aggregates_jackets_and_coats():
    items_all = [
        _item(1, category_key="cat_jackets"),
        _item(2, category_key="cat_coats"),
        _item(3, category_key="cat_blouses"),
    ]

    view = build_dashboard_category_view(items_all, active_cat="cat_outerwear")

    assert view.internal_counts["cat_jackets"] == 1
    assert view.internal_counts["cat_coats"] == 1
    assert view.filter_counts["cat_outerwear"] == 2
    assert [it["id"] for it in view.items] == [1, 2]
    assert view.active_cat_label == "Jacken / Mäntel"



def test_quick_filters_only_include_positive_counts():
    quick = build_quick_filters({"cat_blouses": 2, "cat_outerwear": 1, "cat_tops": 0})

    keys = [entry["key"] for entry in quick]
    assert "cat_blouses" in keys
    assert "cat_outerwear" in keys
    assert "cat_tops" not in keys



def test_filter_dropdown_groups_include_zero_count_options():
    groups = build_filter_dropdown_groups({"cat_blouses": 2})

    apparel = next(group for group in groups if group["label"] == "Bekleidung")
    options = {opt["key"]: opt["count"] for opt in apparel["options"]}

    assert options["cat_blouses"] == 2
    assert options["cat_outerwear"] == 0



def test_filter_items_by_category_returns_all_items_for_empty_active_cat():
    items_all = [_item(1, category_key="cat_blouses"), _item(2, category_key="cat_coats")]

    filtered = filter_items_by_category(items_all, "")

    assert [it["id"] for it in filtered] == [1, 2]



def test_count_internal_categories_ignores_missing_keys():
    counts = count_internal_categories(
        [
            _item(1, category_key="cat_blouses"),
            _item(2, category_key="cat_blouses"),
            _item(3, category_key=None),
        ]
    )

    assert counts == {"cat_blouses": 2}

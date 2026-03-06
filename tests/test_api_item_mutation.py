from src.api_item_mutation import (
    DEFAULT_IMMUTABLE_UPDATE_FIELDS,
    build_create_item_plan,
    build_update_item_plan,
    merge_item_data,
    normalize_item_mutation_payload,
    require_non_empty_update,
)


def test_normalize_item_mutation_payload_drops_unknowns_and_normalizes_values():
    payload = {
        "user_id": " karen ",
        "name": "  Blue Blouse ",
        "needs_review": "yes",
        "unknown": "ignored",
    }

    data = normalize_item_mutation_payload(payload)

    assert data == {
        "user_id": "karen",
        "name": "Blue Blouse",
        "needs_review": 1,
    }



def test_build_create_item_plan_reports_missing_required_fields():
    plan = build_create_item_plan({"user_id": "karen", "name": "   "})

    assert plan.missing_required == ("name",)
    assert not plan.is_valid



def test_build_create_item_plan_keeps_stable_insert_field_order_and_extra_data():
    plan = build_create_item_plan(
        {
            "user_id": "karen",
            "name": "Blue Blouse",
            "brand": "Acme",
        },
        extra_data={"needs_review": 1},
    )

    assert plan.is_valid
    assert plan.fields == ("user_id", "name", "brand", "needs_review")
    assert plan.insert_columns_sql() == "user_id, name, brand, needs_review"
    assert plan.insert_placeholders_sql() == "?, ?, ?, ?"
    assert plan.ordered_params() == ["karen", "Blue Blouse", "Acme", 1]



def test_build_update_item_plan_drops_immutable_user_id_and_preserves_order():
    plan = build_update_item_plan(
        {
            "user_id": "someone-else",
            "name": "Blue Blouse",
            "brand": "Acme",
            "needs_review": "no",
        },
        extra_data={"color_variant": "navy"},
    )

    assert DEFAULT_IMMUTABLE_UPDATE_FIELDS == ("user_id",)
    assert plan.fields == ("name", "brand", "needs_review", "color_variant")
    assert plan.update_assignment_sql() == "name = ?, brand = ?, needs_review = ?, color_variant = ?"
    assert plan.ordered_params() == ["Blue Blouse", "Acme", 0, "navy"]



def test_require_non_empty_update_raises_for_empty_mutation_plan():
    plan = build_update_item_plan({"user_id": "karen"})

    try:
        require_non_empty_update(plan)
    except ValueError as exc:
        assert "No mutable fields supplied for update" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty update plan")



def test_merge_item_data_only_keeps_allowed_fields_and_overrides_updates():
    merged = merge_item_data(
        {"user_id": "karen", "name": "Old", "notes": "before", "x": 1},
        {"name": "New", "notes": None, "y": 2},
    )

    assert merged == {
        "user_id": "karen",
        "name": "New",
        "notes": None,
    }

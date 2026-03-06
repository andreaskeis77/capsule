from src.api_payload_utils import (
    ITEM_MUTATION_SHAPE,
    PayloadShape,
    build_update_assignment_sql,
    extract_known_fields,
    normalize_bool_flag,
    normalize_optional_text,
    normalize_string,
    ordered_params,
    validate_required_fields,
)


def test_normalize_optional_text_and_string():
    assert normalize_optional_text(None) is None
    assert normalize_optional_text("   ") is None
    assert normalize_optional_text("  Foo ") == "Foo"
    assert normalize_string(None) == ""
    assert normalize_string("  Bar ") == "Bar"


def test_normalize_bool_flag_accepts_common_forms():
    assert normalize_bool_flag(True) == 1
    assert normalize_bool_flag(False) == 0
    assert normalize_bool_flag("yes") == 1
    assert normalize_bool_flag("off") == 0
    assert normalize_bool_flag(3) == 1
    assert normalize_bool_flag(0) == 0


def test_extract_known_fields_applies_shape_and_drops_unknown_keys():
    payload = {
        "user_id": " karen ",
        "name": "  Blue Blouse  ",
        "needs_review": "yes",
        "category": "  tops  ",
        "unknown": "ignored",
    }

    data = extract_known_fields(payload, shape=ITEM_MUTATION_SHAPE)

    assert data == {
        "user_id": "karen",
        "name": "Blue Blouse",
        "needs_review": 1,
        "category": "tops",
    }


def test_validate_required_fields_reports_missing_or_blank_values():
    data = {"user_id": "karen", "name": "   ", "brand": None}
    missing = validate_required_fields(data, ITEM_MUTATION_SHAPE.required_fields)
    assert missing == ["name"]


def test_build_update_assignment_sql_and_ordered_params_are_stable():
    data = {"name": "Blue Blouse", "brand": "Acme", "needs_review": 1}
    fields = ["name", "brand", "needs_review"]

    assert build_update_assignment_sql(fields) == "name = ?, brand = ?, needs_review = ?"
    assert ordered_params(data, fields) == ["Blue Blouse", "Acme", 1]


def test_custom_shape_can_include_missing_required_fields_for_create_defaults():
    shape = PayloadShape(
        allowed_fields=("a", "b"),
        required_fields=("a", "b"),
        normalizers={"a": normalize_string},
    )
    data = extract_known_fields({"a": " x "}, shape=shape, include_missing_required=True)
    assert data == {"a": "x", "b": None}

from __future__ import annotations

from src.dashboard_request_state import parse_dashboard_request_state



def _parse_ids(raw):
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip()]



def _normalize_filter_key(raw: str) -> str:
    raw = (raw or "").strip()
    if raw == "cat_outerwear":
        return raw
    if raw == "Jacken & Mäntel":
        return "cat_outerwear"
    return ""



def test_parse_dashboard_request_state_defaults_user_and_empty_modes():
    state = parse_dashboard_request_state(
        {},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.user == "karen"
    assert state.mode == ""
    assert state.ctx == ""
    assert state.review_only is False
    assert state.active_cat == ""
    assert state.selection_mode is False
    assert state.admin_mode is False
    assert state.selected_ids == []



def test_parse_dashboard_request_state_supports_top_alias_for_cat():
    state = parse_dashboard_request_state(
        {"top": "Jacken & Mäntel"},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.cat_raw == "Jacken & Mäntel"
    assert state.active_cat == "cat_outerwear"



def test_parse_dashboard_request_state_prefers_cat_over_legacy_top_alias():
    state = parse_dashboard_request_state(
        {"cat": "cat_outerwear", "top": "Jacken & Mäntel"},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.cat_raw == "cat_outerwear"
    assert state.active_cat == "cat_outerwear"



def test_parse_dashboard_request_state_parses_ids_only_in_selection_mode():
    state = parse_dashboard_request_state(
        {"mode": "select", "ids": "10, 20, 30"},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.selection_mode is True
    assert state.admin_mode is False
    assert state.selected_ids == [10, 20, 30]



def test_parse_dashboard_request_state_does_not_parse_ids_outside_selection_mode():
    state = parse_dashboard_request_state(
        {"mode": "admin", "ids": "10,20,30"},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.selection_mode is False
    assert state.admin_mode is True
    assert state.selected_ids == []



def test_parse_dashboard_request_state_normalizes_user_ctx_and_review():
    state = parse_dashboard_request_state(
        {"user": " Karen ", "ctx": " Business ", "review": "YES"},
        parse_ids_param=_parse_ids,
        normalize_filter_key=_normalize_filter_key,
    )

    assert state.user == "karen"
    assert state.ctx == "business"
    assert state.review_only is True

from __future__ import annotations

from src.web_dashboard_support import build_admin_patch_payload, parse_ids_param


def test_parse_ids_param_deduplicates_filters_and_limits():
    raw = "7, 7, 2, x, -1, 0, 9, 3, 2"
    assert parse_ids_param(raw, limit=3) == [7, 2, 9]


def test_build_admin_patch_payload_normalizes_review_and_drops_empty_strings():
    form = {
        "name": "  Blazer  ",
        "brand": "",
        "needs_review": "on",
        "context": " executive ",
        "notes": "  ",
    }

    payload = build_admin_patch_payload(form)

    assert payload == {
        "name": "Blazer",
        "needs_review": True,
        "context": "executive",
    }

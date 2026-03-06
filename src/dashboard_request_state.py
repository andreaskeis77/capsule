from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Sequence


TRUEISH_REVIEW_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class DashboardRequestState:
    """Normalized dashboard request parameters for the main index view."""

    user: str
    mode: str
    ctx: str
    review_only: bool
    cat_raw: str
    active_cat: str
    ids_raw: str
    selection_mode: bool
    admin_mode: bool
    selected_ids: list[int]


ArgGetter = Mapping[str, str] | object


def _arg_get(args: ArgGetter, key: str, default: str = "") -> str:
    getter = getattr(args, "get", None)
    if callable(getter):
        value = getter(key, default)
    elif isinstance(args, Mapping):
        value = args.get(key, default)
    else:
        value = default
    return "" if value is None else str(value)


def parse_dashboard_request_state(
    args: ArgGetter,
    *,
    parse_ids_param: Callable[[Optional[str]], Sequence[int]],
    normalize_filter_key: Callable[[str], str],
) -> DashboardRequestState:
    """
    Normalize the dashboard request/query parameters.

    Mirrors the current semantics of the Flask dashboard controller:
    - default user is "karen"
    - mode is lower-cased
    - ctx is lower-cased
    - review accepts common truthy string values
    - ?top acts as legacy alias for ?cat when ?cat is empty
    - ids are only parsed in selection mode
    """
    user = _arg_get(args, "user", "karen").strip().lower()
    mode = _arg_get(args, "mode", "").strip().lower()
    ctx = _arg_get(args, "ctx", "").strip().lower()

    review_raw = _arg_get(args, "review", "").strip().lower()
    review_only = review_raw in TRUEISH_REVIEW_VALUES

    cat_raw = _arg_get(args, "cat", "").strip()
    top_raw = _arg_get(args, "top", "").strip()
    if not cat_raw and top_raw:
        cat_raw = top_raw

    active_cat = normalize_filter_key(cat_raw)

    ids_raw = _arg_get(args, "ids", "")
    selection_mode = mode == "select"
    admin_mode = mode == "admin"
    selected_ids = list(parse_ids_param(ids_raw)) if selection_mode else []

    return DashboardRequestState(
        user=user,
        mode=mode,
        ctx=ctx,
        review_only=review_only,
        cat_raw=cat_raw,
        active_cat=active_cat,
        ids_raw=ids_raw,
        selection_mode=selection_mode,
        admin_mode=admin_mode,
        selected_ids=selected_ids,
    )

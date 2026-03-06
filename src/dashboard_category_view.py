from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from src import category_map as cm


Item = Dict[str, object]


@dataclass(frozen=True)
class DashboardCategoryView:
    items_base: List[Item]
    items: List[Item]
    internal_counts: Dict[str, int]
    filter_counts: Dict[str, int]
    quick_filters: List[Dict[str, object]]
    filter_dropdown_groups: List[Dict[str, object]]
    active_cat: str
    active_cat_label: str


def apply_base_filters(items_all: Sequence[Item], ctx: str = "", review_only: bool = False) -> List[Item]:
    items_base = list(items_all)
    if ctx:
        ctx_norm = ctx.strip().lower()
        items_base = [it for it in items_base if str(it.get("context") or "").strip().lower() == ctx_norm]
    if review_only:
        items_base = [it for it in items_base if int(it.get("needs_review") or 0) == 1]
    return items_base



def count_internal_categories(items: Sequence[Item]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for it in items:
        key = it.get("category_key")
        if not key:
            continue
        counts[str(key)] = counts.get(str(key), 0) + 1
    return counts



def build_filter_counts(internal_counts: Dict[str, int]) -> Dict[str, int]:
    return {
        fkey: sum(internal_counts.get(k, 0) for k in match_keys)
        for fkey, match_keys in cm.FILTER_MATCH.items()
    }



def build_quick_filters(filter_counts: Dict[str, int]) -> List[Dict[str, object]]:
    return [
        {"key": key, "label": cm.FILTER_LABEL[key], "count": filter_counts.get(key, 0)}
        for key in cm.QUICK_FILTER_ORDER
        if filter_counts.get(key, 0) > 0
    ]



def build_filter_dropdown_groups(filter_counts: Dict[str, int]) -> List[Dict[str, object]]:
    groups: List[Dict[str, object]] = []
    for group in cm.GROUP_ORDER:
        keys = cm.FILTER_GROUPS.get(group, [])
        groups.append(
            {
                "label": group,
                "options": [
                    {"key": key, "label": cm.FILTER_LABEL[key], "count": filter_counts.get(key, 0)}
                    for key in keys
                ],
            }
        )
    return groups



def filter_items_by_category(items: Sequence[Item], active_cat: str) -> List[Item]:
    if not active_cat:
        return list(items)
    match = cm.FILTER_MATCH.get(active_cat, set())
    return [it for it in items if it.get("category_key") in match]



def build_dashboard_category_view(
    items_all: Sequence[Item],
    *,
    ctx: str = "",
    review_only: bool = False,
    active_cat: str = "",
) -> DashboardCategoryView:
    items_base = apply_base_filters(items_all, ctx=ctx, review_only=review_only)
    internal_counts = count_internal_categories(items_base)
    filter_counts = build_filter_counts(internal_counts)
    quick_filters = build_quick_filters(filter_counts)
    filter_dropdown_groups = build_filter_dropdown_groups(filter_counts)
    items = filter_items_by_category(items_base, active_cat)
    active_cat_label = cm.FILTER_LABEL.get(active_cat, "") if active_cat else ""
    return DashboardCategoryView(
        items_base=items_base,
        items=items,
        internal_counts=internal_counts,
        filter_counts=filter_counts,
        quick_filters=quick_filters,
        filter_dropdown_groups=filter_dropdown_groups,
        active_cat=active_cat,
        active_cat_label=active_cat_label,
    )

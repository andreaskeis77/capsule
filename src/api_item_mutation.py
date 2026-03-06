from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from src.api_payload_utils import (
    ITEM_MUTATION_SHAPE,
    PayloadShape,
    build_update_assignment_sql,
    extract_known_fields,
    ordered_params,
    validate_required_fields,
)


@dataclass(frozen=True)
class ItemMutationPlan:
    """Normalized, order-stable mutation plan for item create/update flows."""

    data: Dict[str, Any]
    fields: tuple[str, ...]
    missing_required: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.missing_required

    def update_assignment_sql(self) -> str:
        return build_update_assignment_sql(self.fields)

    def ordered_params(self) -> list[Any]:
        return ordered_params(self.data, self.fields)

    def insert_columns_sql(self) -> str:
        if not self.fields:
            raise ValueError("No fields to insert")
        return ", ".join(self.fields)

    def insert_placeholders_sql(self) -> str:
        if not self.fields:
            raise ValueError("No fields to insert")
        return ", ".join("?" for _ in self.fields)


DEFAULT_IMMUTABLE_UPDATE_FIELDS: tuple[str, ...] = ("user_id",)


def normalize_item_mutation_payload(
    payload: Mapping[str, Any],
    *,
    shape: PayloadShape = ITEM_MUTATION_SHAPE,
    include_missing_required: bool = False,
) -> Dict[str, Any]:
    """Normalize a raw request payload to the allowed item-mutation fields."""
    return extract_known_fields(
        payload,
        shape=shape,
        include_missing_required=include_missing_required,
    )



def merge_item_data(
    base: Mapping[str, Any],
    updates: Mapping[str, Any],
    *,
    allowed_fields: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Merge two item-like mappings without leaking unexpected keys."""
    if allowed_fields is None:
        allowed = set(ITEM_MUTATION_SHAPE.allowed_fields)
    else:
        allowed = set(allowed_fields)

    merged: Dict[str, Any] = {k: v for k, v in base.items() if k in allowed}
    for key, value in updates.items():
        if key in allowed:
            merged[key] = value
    return merged



def build_create_item_plan(
    payload: Mapping[str, Any],
    *,
    extra_data: Optional[Mapping[str, Any]] = None,
    shape: PayloadShape = ITEM_MUTATION_SHAPE,
) -> ItemMutationPlan:
    """Build a create-plan with normalized data and required-field validation."""
    data = normalize_item_mutation_payload(payload, shape=shape, include_missing_required=True)
    if extra_data:
        data.update(extra_data)

    missing = tuple(validate_required_fields(data, shape.required_fields))
    fields = tuple(field for field in shape.allowed_fields if field in data and data[field] is not None)
    return ItemMutationPlan(data=data, fields=fields, missing_required=missing)



def build_update_item_plan(
    payload: Mapping[str, Any],
    *,
    extra_data: Optional[Mapping[str, Any]] = None,
    shape: PayloadShape = ITEM_MUTATION_SHAPE,
    immutable_fields: Sequence[str] = DEFAULT_IMMUTABLE_UPDATE_FIELDS,
) -> ItemMutationPlan:
    """Build an order-stable update-plan for mutable item fields only.

    The update plan keeps the normalized payload field order and appends injected
    ``extra_data`` fields at the end. This matches the current route behavior
    more closely than re-sorting updates by the canonical payload shape.
    """
    data = normalize_item_mutation_payload(payload, shape=shape, include_missing_required=False)
    for field in immutable_fields:
        data.pop(field, None)

    if extra_data:
        data.update(extra_data)

    fields = tuple(data.keys())
    return ItemMutationPlan(data=data, fields=fields, missing_required=())



def require_non_empty_update(plan: ItemMutationPlan) -> ItemMutationPlan:
    if not plan.fields:
        raise ValueError("No mutable fields supplied for update")
    return plan

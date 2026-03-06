from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Mapping, MutableMapping, Optional, Sequence


Normalizer = Callable[[Any], Any]


def normalize_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_bool_flag(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return 1 if int(value) != 0 else 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "y"}:
        return 1
    if text in {"0", "false", "no", "off", "n", ""}:
        return 0
    raise ValueError(f"Invalid boolean flag: {value!r}")


@dataclass(frozen=True)
class PayloadShape:
    allowed_fields: Sequence[str]
    required_fields: Sequence[str] = ()
    normalizers: Mapping[str, Normalizer] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_fields", tuple(self.allowed_fields))
        object.__setattr__(self, "required_fields", tuple(self.required_fields))
        object.__setattr__(self, "normalizers", dict(self.normalizers or {}))


def extract_known_fields(
    payload: Mapping[str, Any],
    *,
    shape: PayloadShape,
    include_missing_required: bool = False,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for field in shape.allowed_fields:
        if field not in payload:
            continue
        value = payload[field]
        normalizer = shape.normalizers.get(field)
        if normalizer is not None:
            value = normalizer(value)
        out[field] = value

    if include_missing_required:
        for field in shape.required_fields:
            out.setdefault(field, None)
    return out


def validate_required_fields(data: Mapping[str, Any], required_fields: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for field in required_fields:
        value = data.get(field)
        if value is None:
            missing.append(field)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field)
    return missing


def build_update_assignment_sql(fields: Sequence[str]) -> str:
    if not fields:
        raise ValueError("No fields to update")
    return ", ".join(f"{field} = ?" for field in fields)


def ordered_params(data: Mapping[str, Any], fields: Sequence[str]) -> list[Any]:
    return [data[field] for field in fields]


# Wardrobe-specific default shape for v2 item mutations.
ITEM_MUTATION_SHAPE = PayloadShape(
    allowed_fields=(
        "user_id",
        "name",
        "brand",
        "category",
        "color_primary",
        "color_variant",
        "needs_review",
        "context",
        "size",
        "notes",
        "image_path",
    ),
    required_fields=("user_id", "name"),
    normalizers={
        "user_id": normalize_string,
        "name": normalize_string,
        "brand": normalize_optional_text,
        "category": normalize_optional_text,
        "color_primary": normalize_optional_text,
        "color_variant": normalize_optional_text,
        "needs_review": normalize_bool_flag,
        "context": normalize_optional_text,
        "size": normalize_optional_text,
        "notes": normalize_optional_text,
        "image_path": normalize_optional_text,
    },
)

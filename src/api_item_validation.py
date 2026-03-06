from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from PIL import Image


@dataclass(frozen=True)
class PreparedImage:
    raw_bytes: bytes
    jpg_bytes: bytes
    width: Optional[int]
    height: Optional[int]


class ImageDecodeFailure(Exception):
    pass


class ImageTooLargeFailure(Exception):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(f"Image exceeds max size {max_bytes}")
        self.max_bytes = max_bytes


class ImageNormalizeFailure(Exception):
    pass


@dataclass(frozen=True)
class ItemFieldNormalization:
    context: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str]
    needs_review: int
    category: Optional[str] = None
    material_main: Optional[str] = None
    fit: Optional[str] = None
    collar: Optional[str] = None

    def as_extra_data(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "color_primary": self.color_primary,
            "color_variant": self.color_variant,
            "needs_review": self.needs_review,
            "material_main": self.material_main,
            "fit": self.fit,
            "collar": self.collar,
            "context": self.context,
        }


OntologyApplyFn = Callable[[str, Optional[str], str], Tuple[Optional[str], Any]]
ValidateContextFn = Callable[[Optional[str], str], Optional[str]]
DeriveColorFn = Callable[[Optional[str], Optional[str], Optional[str]], Tuple[Optional[str], int]]
DecodeImageFn = Callable[[str], bytes]
NormalizeImageFn = Callable[[bytes], bytes]


def prepare_uploaded_image(
    image_b64: str,
    *,
    max_bytes: int,
    decode_image: DecodeImageFn,
    normalize_image_to_jpg: NormalizeImageFn,
) -> PreparedImage:
    try:
        raw_bytes = decode_image(image_b64)
    except Exception as exc:  # pragma: no cover - caller-specific handling tested via exception type
        raise ImageDecodeFailure() from exc

    if len(raw_bytes) > max_bytes:
        raise ImageTooLargeFailure(max_bytes)

    try:
        jpg_bytes = normalize_image_to_jpg(raw_bytes)
    except Exception as exc:  # pragma: no cover - caller-specific handling tested via exception type
        raise ImageNormalizeFailure() from exc

    width: Optional[int] = None
    height: Optional[int] = None
    try:
        with Image.open(io.BytesIO(jpg_bytes)) as im:
            width, height = im.size
    except Exception:
        pass

    return PreparedImage(raw_bytes=raw_bytes, jpg_bytes=jpg_bytes, width=width, height=height)


def _apply_optional_field(
    field: str,
    value: Optional[str],
    request_id: str,
    *,
    ontology_apply: OntologyApplyFn,
) -> Optional[str]:
    if not value:
        return None
    canonical, _ = ontology_apply(field, value, request_id)
    return canonical


def normalize_create_like_fields(
    payload: Mapping[str, Any],
    request_id: str,
    *,
    ontology_apply: OntologyApplyFn,
    validate_context: ValidateContextFn,
    derive_color_variant_and_review: DeriveColorFn,
) -> ItemFieldNormalization:
    context = validate_context(payload.get("context"), request_id)

    raw_color = payload.get("color_primary")
    canonical_color, _ = ontology_apply("color_primary", raw_color, request_id)
    derived_variant, derived_review = derive_color_variant_and_review(
        raw_color,
        canonical_color,
        payload.get("color_variant"),
    )

    return ItemFieldNormalization(
        context=context,
        category=_apply_optional_field("category", payload.get("category"), request_id, ontology_apply=ontology_apply),
        color_primary=canonical_color,
        color_variant=derived_variant,
        needs_review=int(derived_review),
        material_main=_apply_optional_field(
            "material_main", payload.get("material_main"), request_id, ontology_apply=ontology_apply
        ),
        fit=_apply_optional_field("fit", payload.get("fit"), request_id, ontology_apply=ontology_apply),
        collar=_apply_optional_field("collar", payload.get("collar"), request_id, ontology_apply=ontology_apply),
    )


def normalize_update_fields(
    updates: Mapping[str, Any],
    request_id: str,
    *,
    ontology_apply: OntologyApplyFn,
    validate_context: ValidateContextFn,
    derive_color_variant_and_review: DeriveColorFn,
) -> Dict[str, Any]:
    normalized: Dict[str, Any] = dict(updates)

    if "context" in normalized:
        normalized["context"] = validate_context(normalized.get("context"), request_id)

    if "needs_review" in normalized and normalized["needs_review"] is not None:
        normalized["needs_review"] = int(normalized["needs_review"])

    if "color_primary" in normalized:
        raw_color = normalized.get("color_primary")
        explicit_variant = normalized.get("color_variant")
        canonical_color, _ = ontology_apply("color_primary", raw_color, request_id)
        normalized["color_primary"] = canonical_color
        derived_variant, derived_review = derive_color_variant_and_review(raw_color, canonical_color, explicit_variant)

        if "color_variant" not in normalized:
            normalized["color_variant"] = derived_variant
        if "needs_review" not in normalized:
            normalized["needs_review"] = int(derived_review)

    for field in ("category", "material_main", "fit", "collar"):
        if field in normalized and normalized[field] is not None:
            normalized[field], _ = ontology_apply(field, normalized[field], request_id)

    return normalized

from __future__ import annotations

import base64
import io

from PIL import Image

from src.api_item_validation import (
    ImageDecodeFailure,
    ImageTooLargeFailure,
    normalize_create_like_fields,
    normalize_update_fields,
    prepare_uploaded_image,
)


def _make_jpeg_b64(size: tuple[int, int] = (32, 24)) -> str:
    img = Image.new("RGB", size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _ontology_apply(field: str, value: str | None, request_id: str):
    if value is None:
        return None, {"field": field, "request_id": request_id}
    return f"canon:{field}:{value}", {"field": field, "request_id": request_id}


def _validate_context(value: str | None, request_id: str):
    if value is None:
        return None
    return value.strip().lower() or None


def _derive_color(raw_color: str | None, canonical_color: str | None, explicit_variant: str | None):
    if explicit_variant is not None:
        return explicit_variant.strip() or None, 7
    if raw_color and canonical_color and raw_color != canonical_color:
        return raw_color, 1
    return None, 0


def _decode_image(value: str) -> bytes:
    return base64.b64decode(value)


def _normalize_to_jpg(raw: bytes) -> bytes:
    return raw


def test_prepare_uploaded_image_returns_jpg_bytes_and_dimensions():
    prepared = prepare_uploaded_image(
        _make_jpeg_b64((40, 18)),
        max_bytes=1024 * 1024,
        decode_image=_decode_image,
        normalize_image_to_jpg=_normalize_to_jpg,
    )

    assert prepared.jpg_bytes
    assert prepared.width == 40
    assert prepared.height == 18



def test_prepare_uploaded_image_rejects_large_payload():
    raw = b"x" * 12
    b64 = base64.b64encode(raw).decode("ascii")

    try:
        prepare_uploaded_image(
            b64,
            max_bytes=8,
            decode_image=_decode_image,
            normalize_image_to_jpg=_normalize_to_jpg,
        )
        assert False, "expected ImageTooLargeFailure"
    except ImageTooLargeFailure as exc:
        assert exc.max_bytes == 8



def test_prepare_uploaded_image_raises_decode_failure():
    try:
        prepare_uploaded_image(
            "not-base64",
            max_bytes=1024,
            decode_image=_decode_image,
            normalize_image_to_jpg=_normalize_to_jpg,
        )
        assert False, "expected ImageDecodeFailure"
    except ImageDecodeFailure:
        pass



def test_normalize_create_like_fields_applies_context_and_ontology_fields():
    result = normalize_create_like_fields(
        {
            "context": " Executive ",
            "color_primary": "Blue",
            "category": "Blazer",
            "material_main": "Wool",
            "fit": "Slim",
            "collar": "Shawl",
        },
        "RID-1",
        ontology_apply=_ontology_apply,
        validate_context=_validate_context,
        derive_color_variant_and_review=_derive_color,
    )

    assert result.context == "executive"
    assert result.color_primary == "canon:color_primary:Blue"
    assert result.color_variant == "Blue"
    assert result.needs_review == 1
    assert result.category == "canon:category:Blazer"
    assert result.material_main == "canon:material_main:Wool"
    assert result.fit == "canon:fit:Slim"
    assert result.collar == "canon:collar:Shawl"



def test_normalize_update_fields_preserves_explicit_variant_and_casts_needs_review():
    result = normalize_update_fields(
        {
            "context": " Private ",
            "color_primary": "Blue",
            "color_variant": " Navy ",
            "needs_review": True,
            "category": "Blazer",
        },
        "RID-2",
        ontology_apply=_ontology_apply,
        validate_context=_validate_context,
        derive_color_variant_and_review=_derive_color,
    )

    assert result["context"] == "private"
    assert result["color_primary"] == "canon:color_primary:Blue"
    assert result["color_variant"] == " Navy "
    assert result["needs_review"] == 1
    assert result["category"] == "canon:category:Blazer"

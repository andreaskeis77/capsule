from __future__ import annotations

import base64
import io
from pathlib import Path

import pytest
from PIL import Image

from src.api_item_workflows import (
    InvalidPayloadFieldsError,
    InvalidUserValueError,
    NoFieldsError,
    build_validation_preview,
    prepare_create_item_request,
    prepare_update_item_request,
)
from src.api_payload_utils import ITEM_MUTATION_SHAPE


def _make_test_jpeg_b64(size: tuple[int, int] = (32, 20)) -> str:
    img = Image.new("RGB", size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _decode_image(data: str) -> bytes:
    return base64.b64decode(data)


def _normalize_image_to_jpg(raw: bytes) -> bytes:
    with Image.open(io.BytesIO(raw)) as img:
        out = io.BytesIO()
        img.convert("RGB").save(out, format="JPEG", quality=85)
        return out.getvalue()


def _ontology_apply(field: str, value: str | None, _rid: str):
    return value, None


def _validate_context(value: str | None, _rid: str):
    if value is None:
        return None
    return value.strip().lower()


def _derive_color_variant_and_review(raw_color: str | None, canonical_color: str | None, explicit_variant: str | None):
    return explicit_variant or canonical_color, 0


def _slugify(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def test_prepare_create_item_request_builds_plan_and_image():
    payload = {
        "user_id": "karen",
        "name": "Blue Blazer",
        "context": "Executive",
        "image_main_base64": _make_test_jpeg_b64(),
    }

    prepared = prepare_create_item_request(
        payload,
        "rid-1",
        valid_users=("karen", "andreas"),
        shape=ITEM_MUTATION_SHAPE,
        ontology_apply=_ontology_apply,
        validate_context=_validate_context,
        derive_color_variant_and_review=_derive_color_variant_and_review,
        decode_image=_decode_image,
        normalize_image_to_jpg=_normalize_image_to_jpg,
        max_image_bytes=5_000_000,
    )

    assert prepared.create_plan.is_valid is True
    assert prepared.normalized_fields.context == "executive"
    assert prepared.prepared_image.width == 32
    assert prepared.prepared_image.height == 20


def test_prepare_create_item_request_rejects_invalid_user():
    payload = {"user_id": "nobody", "name": "X", "image_main_base64": _make_test_jpeg_b64()}
    with pytest.raises(InvalidUserValueError):
        prepare_create_item_request(
            payload,
            "rid-1",
            valid_users=("karen",),
            shape=ITEM_MUTATION_SHAPE,
            ontology_apply=_ontology_apply,
            validate_context=_validate_context,
            derive_color_variant_and_review=_derive_color_variant_and_review,
            decode_image=_decode_image,
            normalize_image_to_jpg=_normalize_image_to_jpg,
            max_image_bytes=5_000_000,
        )


def test_prepare_create_item_request_rejects_missing_required_fields():
    payload = {"user_id": "karen", "image_main_base64": _make_test_jpeg_b64()}
    with pytest.raises(InvalidPayloadFieldsError):
        prepare_create_item_request(
            payload,
            "rid-1",
            valid_users=("karen",),
            shape=ITEM_MUTATION_SHAPE,
            ontology_apply=_ontology_apply,
            validate_context=_validate_context,
            derive_color_variant_and_review=_derive_color_variant_and_review,
            decode_image=_decode_image,
            normalize_image_to_jpg=_normalize_image_to_jpg,
            max_image_bytes=5_000_000,
        )


def test_build_validation_preview_returns_expected_shape():
    payload = {"user_id": "karen", "name": "Validate Only", "context": "executive"}
    prepared = prepare_create_item_request(
        {**payload, "image_main_base64": _make_test_jpeg_b64()},
        "rid-99",
        valid_users=("karen",),
        shape=ITEM_MUTATION_SHAPE,
        ontology_apply=_ontology_apply,
        validate_context=_validate_context,
        derive_color_variant_and_review=_derive_color_variant_and_review,
        decode_image=_decode_image,
        normalize_image_to_jpg=_normalize_image_to_jpg,
        max_image_bytes=5_000_000,
    )
    preview = build_validation_preview(
        payload,
        "rid-99",
        normalized_fields=prepared.normalized_fields,
        prepared_image=prepared.prepared_image,
        slugify=_slugify,
        image_max_dim=1600,
    )
    assert preview["ok"] is True
    assert preview["example_image_path"] == "karen/validate-only_NEW"
    assert preview["normalized_image"]["stored_ext"] == "jpg"


def test_prepare_update_item_request_rejects_empty_updates(tmp_path: Path):
    existing = {"id": 1, "user_id": "karen", "name": "Blazer", "image_path": None}
    with pytest.raises(NoFieldsError):
        prepare_update_item_request(
            existing,
            {},
            "rid-1",
            valid_users=("karen",),
            shape=ITEM_MUTATION_SHAPE,
            img_dir=tmp_path,
            ontology_apply=_ontology_apply,
            validate_context=_validate_context,
            derive_color_variant_and_review=_derive_color_variant_and_review,
            logger=__import__("logging").getLogger("test"),
        )

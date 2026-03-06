from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from src.api_item_mutation import ItemMutationPlan, build_create_item_plan, build_update_item_plan, require_non_empty_update
from src.api_item_storage import FolderMoveResult, move_image_folder_for_item
from src.api_item_validation import (
    ItemFieldNormalization,
    PreparedImage,
    normalize_create_like_fields,
    normalize_update_fields,
    prepare_uploaded_image,
)
from src.api_payload_utils import PayloadShape


class InvalidUserValueError(ValueError):
    def __init__(self, user_id: str) -> None:
        super().__init__(user_id)
        self.user_id = user_id


class InvalidPayloadFieldsError(ValueError):
    def __init__(self, missing_fields: Sequence[str]) -> None:
        super().__init__(", ".join(missing_fields))
        self.missing_fields = tuple(missing_fields)


class NoFieldsError(ValueError):
    pass


class NoValidFieldsError(ValueError):
    pass


@dataclass(frozen=True)
class PreparedCreateRequest:
    normalized_fields: ItemFieldNormalization
    create_plan: ItemMutationPlan
    prepared_image: PreparedImage


@dataclass(frozen=True)
class PreparedUpdateRequest:
    updates: Dict[str, Any]
    update_plan: ItemMutationPlan
    move_result: Optional[FolderMoveResult]


OntologyApplyFn = Callable[[str, Optional[str], str], Tuple[Optional[str], Any]]
ValidateContextFn = Callable[[Optional[str], str], Optional[str]]
DeriveColorFn = Callable[[Optional[str], Optional[str], Optional[str]], Tuple[Optional[str], int]]
DecodeImageFn = Callable[[str], bytes]
NormalizeImageFn = Callable[[bytes], bytes]
SlugifyFn = Callable[[str], str]


def ensure_valid_user(user_id: str, *, valid_users: Sequence[str]) -> str:
    if user_id not in set(valid_users):
        raise InvalidUserValueError(user_id)
    return user_id


def prepare_create_item_request(
    payload_data: Mapping[str, Any],
    request_id: str,
    *,
    valid_users: Sequence[str],
    shape: PayloadShape,
    ontology_apply: OntologyApplyFn,
    validate_context: ValidateContextFn,
    derive_color_variant_and_review: DeriveColorFn,
    decode_image: DecodeImageFn,
    normalize_image_to_jpg: NormalizeImageFn,
    max_image_bytes: int,
) -> PreparedCreateRequest:
    ensure_valid_user(str(payload_data.get("user_id") or ""), valid_users=valid_users)

    normalized_fields = normalize_create_like_fields(
        payload_data,
        request_id,
        ontology_apply=ontology_apply,
        validate_context=validate_context,
        derive_color_variant_and_review=derive_color_variant_and_review,
    )

    create_plan = build_create_item_plan(
        payload_data,
        extra_data=normalized_fields.as_extra_data(),
        shape=shape,
    )
    if not create_plan.is_valid:
        raise InvalidPayloadFieldsError(create_plan.missing_required)

    prepared_image = prepare_uploaded_image(
        str(payload_data.get("image_main_base64") or ""),
        max_bytes=max_image_bytes,
        decode_image=decode_image,
        normalize_image_to_jpg=normalize_image_to_jpg,
    )
    return PreparedCreateRequest(
        normalized_fields=normalized_fields,
        create_plan=create_plan,
        prepared_image=prepared_image,
    )


def build_validation_preview(
    payload_data: Mapping[str, Any],
    request_id: str,
    *,
    normalized_fields: ItemFieldNormalization,
    prepared_image: PreparedImage,
    slugify: SlugifyFn,
    image_max_dim: int,
) -> Dict[str, Any]:
    user_id = str(payload_data.get("user_id") or "")
    name = str(payload_data.get("name") or "")
    slug = slugify(name)
    example_rel = str(Path(user_id) / f"{slug}_NEW").replace("\\", "/")

    return {
        "ok": True,
        "request_id": request_id,
        "example_image_path": example_rel,
        "normalized_fields": {
            "user_id": user_id,
            "name": name,
            "brand": payload_data.get("brand"),
            "category": normalized_fields.category,
            "color_primary": normalized_fields.color_primary,
            "color_variant": normalized_fields.color_variant,
            "needs_review": int(normalized_fields.needs_review),
            "material_main": normalized_fields.material_main,
            "fit": normalized_fields.fit,
            "collar": normalized_fields.collar,
            "price": payload_data.get("price"),
            "vision_description": payload_data.get("vision_description"),
            "context": normalized_fields.context,
            "size": payload_data.get("size"),
            "notes": payload_data.get("notes"),
        },
        "normalized_image": {
            "stored_ext": "jpg",
            "bytes": len(prepared_image.jpg_bytes),
            "width": prepared_image.width,
            "height": prepared_image.height,
            "max_dim": image_max_dim,
        },
    }


def prepare_update_item_request(
    existing: Mapping[str, Any],
    payload_updates: Mapping[str, Any],
    request_id: str,
    *,
    valid_users: Sequence[str],
    shape: PayloadShape,
    img_dir: Path,
    ontology_apply: OntologyApplyFn,
    validate_context: ValidateContextFn,
    derive_color_variant_and_review: DeriveColorFn,
    logger: logging.Logger,
) -> PreparedUpdateRequest:
    existing_map: Dict[str, Any] = dict(existing)
    updates: Dict[str, Any] = dict(payload_updates)
    if not updates:
        raise NoFieldsError("No fields supplied for update")

    updates = normalize_update_fields(
        updates,
        request_id,
        ontology_apply=ontology_apply,
        validate_context=validate_context,
        derive_color_variant_and_review=derive_color_variant_and_review,
    )

    old_rel = existing_map.get("image_path")
    move_result: Optional[FolderMoveResult] = None

    if old_rel and ("name" in updates or "user_id" in updates):
        old_user = existing_map["user_id"]
        old_name = existing_map["name"]
        old_id = existing_map["id"]

        new_user = updates.get("user_id", old_user)
        new_name = updates.get("name", old_name)
        ensure_valid_user(str(new_user), valid_users=valid_users)

        try:
            move_result = move_image_folder_for_item(img_dir, str(old_rel), str(new_user), str(new_name), int(old_id))
            if move_result.conflict:
                logger.warning(
                    "Folder move skipped (destination exists)",
                    extra={"request_id": request_id, "event": "item.update.move_skipped", "src": old_rel, "dst": move_result.new_rel},
                )
            elif move_result.moved:
                updates["image_path"] = move_result.new_rel
                logger.info(
                    "Moved image folder",
                    extra={"request_id": request_id, "event": "item.update.move_ok", "src": old_rel, "dst": move_result.new_rel, "item_id": old_id},
                )
        except Exception:
            logger.exception(
                "Folder move failed (continuing metadata update)",
                extra={"request_id": request_id, "event": "item.update.move_failed", "item_id": old_id},
            )
            updates.pop("image_path", None)
            move_result = None

    update_plan = build_update_item_plan(updates, shape=shape, immutable_fields=())
    try:
        require_non_empty_update(update_plan)
    except ValueError as exc:
        raise NoValidFieldsError(str(exc)) from exc

    return PreparedUpdateRequest(updates=updates, update_plan=update_plan, move_result=move_result)

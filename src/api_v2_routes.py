from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src import settings
from src.api_item_query import (
    count_review_rows,
    fetch_item_image_ref_by_id,
    fetch_item_row_by_id,
    item_row_to_payload,
    item_summary_row_to_payload,
    list_item_summary_rows,
    list_review_rows,
)
from src.api_item_review import build_review_items
from src.api_item_storage import (
    cleanup_trashed_image_dir,
    create_image_folder_for_item,
    move_item_image_dir_to_trash,
    rollback_moved_image_dir,
    rollback_trashed_image_dir,
)
from src.api_item_validation import ImageDecodeFailure, ImageNormalizeFailure, ImageTooLargeFailure
from src.api_item_workflows import (
    InvalidPayloadFieldsError,
    InvalidUserValueError,
    NoFieldsError,
    NoValidFieldsError,
    build_validation_preview,
    prepare_create_item_request,
    prepare_update_item_request,
)
from src.api_v2_contracts import (
    API_V2_ITEM_MUTATION_SHAPE,
    DeleteResponse,
    ItemCreateRequest,
    ItemResponse,
    ItemSummary,
    ItemUpdateRequest,
    ListItemsResponse,
    ReviewItem,
    ReviewQueueResponse,
    VALID_USERS,
)
import src.api_v2_runtime as runtime

router = APIRouter(prefix="/api/v2")


@router.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


def _row_to_item(row: sqlite3.Row, base_url: str) -> ItemResponse:
    return ItemResponse(**item_row_to_payload(row, base_url))


@router.get("/items", response_model=ListItemsResponse, dependencies=[Depends(runtime.require_api_key)])
def list_items(request: Request, user: str) -> ListItemsResponse:
    rid = runtime._request_id(request)
    if user not in VALID_USERS:
        runtime._raise(400, rid, "InvalidUser", field="user", value=user)

    try:
        conn = runtime.db_conn()
        rows = list_item_summary_rows(conn, user)
    except Exception as exc:
        runtime._handle_db_exc(exc, rid, op="items.list", default_error="ListFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    items = [ItemSummary(**item_summary_row_to_payload(row)) for row in rows]
    return ListItemsResponse(user=user, items=items)


@router.get("/items/review", response_model=ReviewQueueResponse, dependencies=[Depends(runtime.require_api_key)])
def review_queue(
    request: Request,
    user: str,
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ReviewQueueResponse:
    rid = runtime._request_id(request)
    if user not in VALID_USERS:
        runtime._raise(400, rid, "InvalidUser", field="user", value=user)

    try:
        conn = runtime.db_conn()
        total = count_review_rows(conn, user)
        rows = list_review_rows(conn, user, limit, offset)
    except Exception as exc:
        runtime._handle_db_exc(exc, rid, op="items.review_queue", default_error="ReviewQueueFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    items = [
        ReviewItem(**payload)
        for payload in build_review_items(rows, ontology=runtime.ONTOLOGY, request_id=rid, logger=runtime.logger)
    ]
    return ReviewQueueResponse(user=user, total=total, items=items)


@router.get("/items/{item_id}", response_model=ItemResponse, dependencies=[Depends(runtime.require_api_key)])
def get_item(request: Request, item_id: int) -> ItemResponse:
    rid = runtime._request_id(request)

    try:
        conn = runtime.db_conn()
        row = fetch_item_row_by_id(conn, item_id)
    except Exception as exc:
        runtime._handle_db_exc(exc, rid, op="items.get", default_error="GetFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    if not row:
        runtime._raise(404, rid, "NotFound", item_id=item_id)

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.post("/items", response_model=ItemResponse, dependencies=[Depends(runtime.require_api_key)])
def create_item(request: Request, payload: ItemCreateRequest) -> ItemResponse:
    rid = runtime._request_id(request)

    try:
        prepared = prepare_create_item_request(
            payload.model_dump(),
            rid,
            valid_users=tuple(sorted(VALID_USERS)),
            shape=API_V2_ITEM_MUTATION_SHAPE,
            ontology_apply=runtime._ontology_apply,
            validate_context=runtime._validate_context,
            derive_color_variant_and_review=runtime._derive_color_variant_and_review,
            decode_image=runtime._decode_image_base64,
            normalize_image_to_jpg=runtime._normalize_image_to_jpg,
            max_image_bytes=settings.MAX_IMAGE_BYTES,
        )
    except InvalidUserValueError as exc:
        runtime._raise(400, rid, "InvalidUser", field="user_id", value=exc.user_id)
    except InvalidPayloadFieldsError as exc:
        runtime._raise(400, rid, "InvalidPayload", fields=list(exc.missing_fields))
    except ImageDecodeFailure:
        runtime.logger.exception(
            "Image base64 decode failed",
            extra={"request_id": rid, "event": "item.create.image_decode"},
        )
        runtime._raise(400, rid, "ImageDecodeFailed", stage="base64")
    except ImageTooLargeFailure as exc:
        runtime._raise(413, rid, "ImageTooLarge", stage="image", max_bytes=exc.max_bytes)
    except ImageNormalizeFailure:
        runtime.logger.exception(
            "Image normalize failed",
            extra={"request_id": rid, "event": "item.create.image_normalize"},
        )
        runtime._raise(400, rid, "ImageDecodeFailed", stage="image")

    runtime.logger.info(
        "Create normalization",
        extra={
            "request_id": rid,
            "event": "item.create.normalize",
            "color_primary": prepared.normalized_fields.color_primary,
            "color_variant": prepared.normalized_fields.color_variant,
            "needs_review": prepared.normalized_fields.needs_review,
            "context": prepared.normalized_fields.context,
        },
    )

    conn = runtime.db_conn()
    cur = conn.cursor()
    item_id: Optional[int] = None
    created_image = None

    try:
        cur.execute(
            f"INSERT INTO items ({prepared.create_plan.insert_columns_sql()}) VALUES ({prepared.create_plan.insert_placeholders_sql()})",
            prepared.create_plan.ordered_params(),
        )
        item_id = int(cur.lastrowid)

        created_image = create_image_folder_for_item(
            settings.IMG_DIR,
            payload.user_id,
            payload.name,
            item_id,
            prepared.prepared_image.jpg_bytes,
        )
        cur.execute("UPDATE items SET image_path = ? WHERE id = ?", (created_image.rel_path, item_id))
        conn.commit()

        runtime.logger.info(
            "Create OK",
            extra={
                "request_id": rid,
                "event": "item.create.ok",
                "item_id": item_id,
                "image_path": created_image.rel_path,
            },
        )
    except Exception as exc:
        conn.rollback()

        try:
            if item_id is not None:
                cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
                conn.commit()
        except Exception:
            pass

        try:
            if created_image is not None and created_image.abs_dir.exists():
                shutil.rmtree(created_image.abs_dir, ignore_errors=True)
        except Exception:
            runtime.logger.exception(
                "Create cleanup failed",
                extra={"request_id": rid, "event": "item.create.cleanup"},
            )

        if runtime._is_db_locked(exc):
            runtime._raise(503, rid, "DbLocked", stage="db", op="items.create")

        runtime.logger.exception("Create failed", extra={"request_id": rid, "event": "item.create.failed"})
        runtime._raise(500, rid, "CreateFailed", stage="db", op="items.create")
    finally:
        conn.close()

    try:
        conn2 = runtime.db_conn()
        row = fetch_item_row_by_id(conn2, item_id)
        conn2.close()
    except Exception as exc:
        runtime._handle_db_exc(exc, rid, op="items.create.fetch", default_error="CreateFailed")
        raise

    if not row:
        runtime._raise(500, rid, "CreateFailed", stage="db", reason="missing_row_after_create")

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.post("/items/validate", dependencies=[Depends(runtime.require_api_key)])
def validate_item(request: Request, payload: ItemCreateRequest) -> Dict[str, Any]:
    rid = runtime._request_id(request)

    try:
        prepared = prepare_create_item_request(
            payload.model_dump(),
            rid,
            valid_users=tuple(sorted(VALID_USERS)),
            shape=API_V2_ITEM_MUTATION_SHAPE,
            ontology_apply=runtime._ontology_apply,
            validate_context=runtime._validate_context,
            derive_color_variant_and_review=runtime._derive_color_variant_and_review,
            decode_image=runtime._decode_image_base64,
            normalize_image_to_jpg=runtime._normalize_image_to_jpg,
            max_image_bytes=settings.MAX_IMAGE_BYTES,
        )
    except InvalidUserValueError as exc:
        runtime._raise(400, rid, "InvalidUser", field="user_id", value=exc.user_id)
    except InvalidPayloadFieldsError as exc:
        runtime._raise(400, rid, "InvalidPayload", fields=list(exc.missing_fields))
    except ImageDecodeFailure:
        runtime.logger.exception(
            "Validate image base64 decode failed",
            extra={"request_id": rid, "event": "item.validate.image_decode"},
        )
        runtime._raise(400, rid, "ImageDecodeFailed", stage="base64")
    except ImageTooLargeFailure as exc:
        runtime._raise(413, rid, "ImageTooLarge", stage="image", max_bytes=exc.max_bytes)
    except ImageNormalizeFailure:
        runtime.logger.exception(
            "Validate image normalize failed",
            extra={"request_id": rid, "event": "item.validate.image_normalize"},
        )
        runtime._raise(400, rid, "ImageDecodeFailed", stage="image")

    return build_validation_preview(
        payload.model_dump(),
        rid,
        normalized_fields=prepared.normalized_fields,
        prepared_image=prepared.prepared_image,
        slugify=runtime._slugify,
        image_max_dim=settings.IMAGE_MAX_DIM,
    )


@router.patch("/items/{item_id}", response_model=ItemResponse, dependencies=[Depends(runtime.require_api_key)])
def update_item(request: Request, item_id: int, payload: ItemUpdateRequest) -> ItemResponse:
    rid = runtime._request_id(request)
    conn = runtime.db_conn()
    cur = conn.cursor()

    try:
        existing = fetch_item_row_by_id(conn, item_id)
    except Exception as exc:
        conn.close()
        runtime._handle_db_exc(exc, rid, op="items.update.load", default_error="UpdateFailed")
        raise

    if not existing:
        conn.close()
        runtime._raise(404, rid, "NotFound", item_id=item_id)

    try:
        prepared = prepare_update_item_request(
            existing,
            payload.model_dump(exclude_unset=True),
            rid,
            valid_users=tuple(sorted(VALID_USERS)),
            shape=API_V2_ITEM_MUTATION_SHAPE,
            img_dir=settings.IMG_DIR,
            ontology_apply=runtime._ontology_apply,
            validate_context=runtime._validate_context,
            derive_color_variant_and_review=runtime._derive_color_variant_and_review,
            logger=runtime.logger,
        )
    except NoFieldsError:
        conn.close()
        runtime._raise(400, rid, "NoFields")
    except NoValidFieldsError:
        conn.close()
        runtime._raise(400, rid, "NoValidFields")
    except InvalidUserValueError as exc:
        conn.close()
        runtime._raise(400, rid, "InvalidUser", field="user_id", value=exc.user_id)

    if "color_primary" in prepared.updates:
        runtime.logger.info(
            "Update color",
            extra={
                "request_id": rid,
                "event": "item.update.color",
                "item_id": item_id,
                "color_primary": prepared.updates.get("color_primary"),
                "color_variant": prepared.updates.get("color_variant"),
                "needs_review": prepared.updates.get("needs_review"),
            },
        )

    sql = f"UPDATE items SET {prepared.update_plan.update_assignment_sql()} WHERE id = ?"
    params = [*prepared.update_plan.ordered_params(), item_id]

    try:
        cur.execute(sql, params)
        conn.commit()
        runtime.logger.info(
            "Update OK",
            extra={"request_id": rid, "event": "item.update.ok", "item_id": item_id},
        )
    except Exception as exc:
        conn.rollback()

        if prepared.move_result and prepared.move_result.moved:
            try:
                rollback_moved_image_dir(prepared.move_result)
                runtime.logger.warning(
                    "Rolled back folder move after DB failure",
                    extra={"request_id": rid, "event": "item.update.move_rollback", "item_id": item_id},
                )
            except Exception:
                runtime.logger.exception(
                    "Rollback of folder move failed",
                    extra={"request_id": rid, "event": "item.update.move_rollback_failed", "item_id": item_id},
                )

        if runtime._is_db_locked(exc):
            runtime._raise(503, rid, "DbLocked", stage="db", op="items.update")

        runtime.logger.exception(
            "Update failed",
            extra={"request_id": rid, "event": "item.update.failed", "item_id": item_id},
        )
        runtime._raise(500, rid, "UpdateFailed", stage="db", op="items.update")
    finally:
        conn.close()

    try:
        conn2 = runtime.db_conn()
        row = fetch_item_row_by_id(conn2, item_id)
        conn2.close()
    except Exception as exc:
        runtime._handle_db_exc(exc, rid, op="items.update.fetch", default_error="UpdateFailed")
        raise

    if not row:
        runtime._raise(500, rid, "UpdateFailed", stage="db", reason="missing_row_after_update")

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.delete("/items/{item_id}", response_model=DeleteResponse, dependencies=[Depends(runtime.require_api_key)])
def delete_item(request: Request, item_id: int) -> DeleteResponse:
    rid = runtime._request_id(request)
    conn = runtime.db_conn()
    cur = conn.cursor()

    try:
        row = fetch_item_image_ref_by_id(conn, item_id)
    except Exception as exc:
        conn.close()
        runtime._handle_db_exc(exc, rid, op="items.delete.load", default_error="DeleteFailed")
        raise

    if not row:
        conn.close()
        runtime._raise(404, rid, "NotFound", item_id=item_id)

    image_path = (row["image_path"] or "").strip()
    trash_result = None

    try:
        if image_path:
            try:
                trash_result = move_item_image_dir_to_trash(
                    settings.IMG_DIR,
                    settings.TRASH_DIR,
                    image_path,
                    item_id,
                    rid,
                )
            except RuntimeError as exc:
                if str(exc) == "JailCheckFailed":
                    runtime._raise(400, rid, "JailCheckFailed", stage="fs", op="items.delete")
                raise

        cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()

        runtime.logger.info(
            "Delete OK",
            extra={"request_id": rid, "event": "item.delete.ok", "item_id": item_id, "image_path": image_path},
        )
    except HTTPException:
        if trash_result and trash_result.moved:
            try:
                rollback_trashed_image_dir(trash_result)
            except Exception:
                runtime.logger.exception(
                    "Rollback move failed after HTTPException",
                    extra={"request_id": rid, "event": "item.delete.rollback_failed"},
                )
        raise
    except Exception as exc:
        conn.rollback()

        if trash_result and trash_result.moved:
            try:
                rollback_trashed_image_dir(trash_result)
            except Exception:
                runtime.logger.exception(
                    "Rollback move failed after DeleteFailed",
                    extra={"request_id": rid, "event": "item.delete.rollback_failed"},
                )

        if runtime._is_db_locked(exc):
            runtime._raise(503, rid, "DbLocked", stage="db", op="items.delete")

        runtime.logger.exception(
            "Delete failed",
            extra={"request_id": rid, "event": "item.delete.failed", "item_id": item_id},
        )
        runtime._raise(500, rid, "DeleteFailed", stage="db", op="items.delete")
    finally:
        conn.close()

    if trash_result and trash_result.moved:
        try:
            cleanup_trashed_image_dir(trash_result)
        except Exception:
            runtime.logger.exception(
                "Trash cleanup failed (best effort)",
                extra={"request_id": rid, "event": "item.delete.trash_cleanup_failed"},
            )

    return DeleteResponse(deleted=True, id=item_id, image_path=image_path)

from __future__ import annotations

import src.api_v2_runtime as _runtime
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
    VALID_CONTEXTS,
    VALID_USERS,
)
from src.api_v2_routes import (
    create_item,
    delete_item,
    get_item,
    health,
    list_items,
    review_queue,
    router,
    update_item,
    validate_item,
)
from src.api_v2_runtime import (
    db_conn,
    logger,
    require_api_key,
    _decode_image_base64,
    _derive_color_variant_and_review,
    _detail,
    _handle_db_exc,
    _is_db_locked,
    _normalize_context,
    _normalize_image_to_jpg,
    _ontology_apply,
    _raise,
    _request_id,
    _require_valid_user,
    _rmtree_robust,
    _safe_under,
    _slugify,
    _validate_context,
)

# Re-exported runtime state. Kept in sync by the wrapper below.
ONTOLOGY = _runtime.ONTOLOGY


def init_ontology() -> None:
    _runtime.init_ontology()
    globals()["ONTOLOGY"] = _runtime.ONTOLOGY


__all__ = [
    "API_V2_ITEM_MUTATION_SHAPE",
    "DeleteResponse",
    "ItemCreateRequest",
    "ItemResponse",
    "ItemSummary",
    "ItemUpdateRequest",
    "ListItemsResponse",
    "ReviewItem",
    "ReviewQueueResponse",
    "VALID_CONTEXTS",
    "VALID_USERS",
    "create_item",
    "db_conn",
    "delete_item",
    "get_item",
    "health",
    "init_ontology",
    "list_items",
    "logger",
    "require_api_key",
    "review_queue",
    "router",
    "update_item",
    "validate_item",
    "_decode_image_base64",
    "_derive_color_variant_and_review",
    "_detail",
    "_handle_db_exc",
    "_is_db_locked",
    "_normalize_context",
    "_normalize_image_to_jpg",
    "_ontology_apply",
    "_raise",
    "_request_id",
    "_require_valid_user",
    "_rmtree_robust",
    "_safe_under",
    "_slugify",
    "_validate_context",
    "ONTOLOGY",
]

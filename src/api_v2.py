# FILE: src/api_v2.py
from __future__ import annotations

import base64
import io
import logging
import os
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field
from PIL import Image

from src import settings
from src.api_item_mutation import build_create_item_plan, build_update_item_plan, require_non_empty_update
from src.api_item_storage import (
    cleanup_trashed_image_dir,
    create_image_folder_for_item,
    move_image_folder_for_item,
    move_item_image_dir_to_trash,
    rollback_moved_image_dir,
    rollback_trashed_image_dir,
)
from src.api_payload_utils import PayloadShape, normalize_bool_flag
from src.error_contract import error_class_for_status
from src.ontology_runtime import OntologyManager, NormalizationResult

logger = logging.getLogger("WardrobeControl")
router = APIRouter(prefix="/api/v2")

ONTOLOGY: Optional[OntologyManager] = None
VALID_USERS = {"andreas", "karen"}
VALID_CONTEXTS = {"private", "executive"}  # wardrobe usage context

API_V2_ITEM_MUTATION_SHAPE = PayloadShape(
    allowed_fields=(
        "user_id", "name", "brand", "category", "color_primary", "color_variant", "needs_review",
        "material_main", "fit", "collar", "price", "vision_description", "image_path", "context", "size", "notes",
    ),
    required_fields=("user_id", "name"),
    normalizers={"needs_review": normalize_bool_flag},
)


# -------------------------
# Helpers: request_id, errors, db classification
# -------------------------

def _request_id(request: Request) -> str:
    return request.state.request_id if hasattr(request.state, "request_id") else "-"


def _detail(status_code: int, request_id: str, error: str, **extra: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "error": error,
        "request_id": request_id,
        "error_class": error_class_for_status(status_code),
    }
    d.update(extra)
    return d


def _raise(status_code: int, request_id: str, error: str, **extra: Any) -> None:
    raise HTTPException(status_code=status_code, detail=_detail(status_code, request_id, error, **extra))


def _is_db_locked(exc: BaseException) -> bool:
    if not isinstance(exc, sqlite3.OperationalError):
        return False
    msg = str(exc).lower()
    return ("database is locked" in msg) or ("locked" in msg) or ("busy" in msg)


def _handle_db_exc(exc: BaseException, rid: str, *, op: str, default_error: str) -> None:
    if _is_db_locked(exc):
        logger.warning(
            "DB locked/busy",
            extra={"request_id": rid, "event": "db.locked", "op": op},
        )
        _raise(503, rid, "DbLocked", stage="db", op=op)

    logger.exception(
        "DB error",
        extra={"request_id": rid, "event": "db.error", "op": op},
    )
    _raise(500, rid, default_error, stage="db", op=op)


def _require_valid_user(user_id: str, rid: str) -> None:
    if user_id not in VALID_USERS:
        _raise(400, rid, "InvalidUser", field="user_id", value=user_id)


def _normalize_context(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = value.strip().lower()
    return v or None


def _validate_context(value: Optional[str], rid: str) -> Optional[str]:
    v = _normalize_context(value)
    if v is None:
        return None
    if v not in VALID_CONTEXTS:
        _raise(400, rid, "InvalidContext", field="context", value=value, allowed=sorted(list(VALID_CONTEXTS)))
    return v


# -------------------------
# Ontology init (signature tolerant)
# -------------------------

def init_ontology() -> None:
    """
    Load ontology in a signature-tolerant way.
    Some versions accept extra tuning kwargs, others accept none.
    """
    global ONTOLOGY

    if settings.ONTOLOGY_MODE == "off":
        ONTOLOGY = None
        logger.info("Ontology disabled (mode=off)", extra={"request_id": "-", "event": "ontology.off"})
        return

    try:
        import inspect

        sig = inspect.signature(OntologyManager.load_from_files)
        kwargs: Dict[str, Any] = {}

        if "suggest_threshold" in sig.parameters:
            kwargs["suggest_threshold"] = settings.SUGGEST_THRESHOLD
        if "allow_legacy" in sig.parameters:
            kwargs["allow_legacy"] = settings.ONTOLOGY_ALLOW_LEGACY
        if "tolerant_fields" in sig.parameters:
            kwargs["tolerant_fields"] = settings.ONTOLOGY_TOLERANT_FIELDS

        if "ontology_dir" in sig.parameters:
            kwargs["ontology_dir"] = settings.ONTOLOGY_DIR
        if "overrides_file" in sig.parameters:
            kwargs["overrides_file"] = settings.ONTOLOGY_OVERRIDES_FILE
        if "color_lexicon_file" in sig.parameters:
            kwargs["color_lexicon_file"] = settings.ONTOLOGY_COLOR_LEXICON_FILE

        ONTOLOGY = OntologyManager.load_from_files(**kwargs)  # type: ignore[arg-type]
        logger.info(
            "Ontology loaded",
            extra={
                "request_id": "-",
                "event": "ontology.loaded",
                "mode": settings.ONTOLOGY_MODE,
                "allow_legacy": settings.ONTOLOGY_ALLOW_LEGACY,
                "tolerant_fields": sorted(settings.ONTOLOGY_TOLERANT_FIELDS),
            },
        )
    except Exception as e:
        ONTOLOGY = None
        logger.warning(
            f"Ontology init failed; continuing without ontology. Error: {e}",
            extra={"request_id": "-", "event": "ontology.init_failed"},
            exc_info=True,
        )


# -------------------------
# Auth / DB / misc helpers
# -------------------------

def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> None:
    rid = _request_id(request)

    if settings.ALLOW_LOCAL_NOAUTH and request.client and request.client.host in {"127.0.0.1", "::1"}:
        return

    if not settings.API_KEY:
        _raise(500, rid, "ServerMisconfigured", stage="auth", reason="missing_api_key")

    if not x_api_key or x_api_key.strip() != settings.API_KEY:
        _raise(401, rid, "Unauthorized", stage="auth")


def db_conn() -> sqlite3.Connection:
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("Ã¤", "ae")
        .replace("Ã¶", "oe")
        .replace("Ã¼", "ue")
        .replace("ÃŸ", "ss")
    )
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "item"


def _safe_under(base: Path, target: Path) -> bool:
    try:
        base_r = base.resolve()
        targ_r = target.resolve()
        if hasattr(targ_r, "is_relative_to"):
            return targ_r.is_relative_to(base_r)  # type: ignore[attr-defined]
        targ_r.relative_to(base_r)
        return True
    except Exception:
        return False


def _decode_image_base64(data: str) -> bytes:
    if not data:
        raise ValueError("image_main_base64 is empty")
    s = data.strip()
    if s.startswith("data:"):
        comma = s.find(",")
        if comma == -1:
            raise ValueError("Invalid data URL")
        s = s[comma + 1 :]
    return base64.b64decode(s, validate=False)


def _normalize_image_to_jpg(raw: bytes) -> bytes:
    with Image.open(io.BytesIO(raw)) as img:
        img = img.convert("RGB")
        img.thumbnail((settings.IMAGE_MAX_DIM, settings.IMAGE_MAX_DIM))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=settings.IMAGE_JPEG_QUALITY, optimize=True)
        return out.getvalue()


def _rmtree_robust(path: Path | str, ignore_errors: bool = False) -> None:
    path = Path(path)
    import stat
    import time
    import inspect

    has_onexc = "onexc" in inspect.signature(shutil.rmtree).parameters

    def _make_writable(p) -> None:
        try:
            os.chmod(p, stat.S_IWRITE)
        except Exception:
            pass

    def _onerror(func, p, exc_info):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    def _onexc(func, p, exc):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    for attempt in range(3):
        try:
            if not path.exists():
                return
            if has_onexc:
                shutil.rmtree(path, onexc=_onexc)
            else:
                shutil.rmtree(path, onerror=_onerror)
            return
        except Exception:
            if attempt == 2:
                if ignore_errors:
                    return
                raise
            time.sleep(0.2 * (attempt + 1))


# -------------------------
# Ontology helpers
# -------------------------

def _ontology_apply(field: str, value: Optional[str], request_id: str) -> Tuple[Optional[str], NormalizationResult]:
    if ONTOLOGY is None:
        nr = NormalizationResult(
            field=field,
            original=value or "",
            canonical=value,
            matched_by="none",
            confidence=0.0,
            suggestions=[],
            meta=None,
        )
        return value, nr

    canonical, nr = ONTOLOGY.validate_or_normalize(field, value)

    if settings.ONTOLOGY_MODE == "soft" and canonical is None and field in settings.ONTOLOGY_TOLERANT_FIELDS:
        logger.info(
            "Ontology tolerant miss",
            extra={"request_id": request_id, "event": "ontology.tolerant_miss", "field": field, "value": value},
        )
        return None, nr

    if settings.ONTOLOGY_MODE in {"soft", "strict"} and canonical is None:
        detail = _detail(
            400,
            request_id,
            "OntologyValidationError",
            field=field,
            value=value,
            suggestions=[
                {"canonical": s.canonical, "score": s.score, "label": s.label} for s in (nr.suggestions or [])
            ],
        )
        raise HTTPException(status_code=400, detail=detail)

    return canonical, nr


def _derive_color_variant_and_review(
    raw_color: Optional[str],
    canonical_color: Optional[str],
    explicit_variant: Optional[str],
) -> Tuple[Optional[str], int]:
    raw = (raw_color or "").strip()
    canon = (canonical_color or "").strip()

    if explicit_variant is not None:
        v = explicit_variant.strip() or None
        needs_review = 1 if (raw and canon and raw.lower() != canon.lower()) else 0
        return v, needs_review

    if raw and canon and raw.lower() != canon.lower():
        return raw, 1

    return None, 0


# -------------------------
# Models
# -------------------------

class ItemCreateRequest(BaseModel):
    user_id: str = Field(..., description="andreas|karen")
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    color_primary: Optional[str] = None
    color_variant: Optional[str] = None
    material_main: Optional[str] = None
    fit: Optional[str] = None
    collar: Optional[str] = None
    price: Optional[str] = None
    vision_description: Optional[str] = None

    # NEW: planning/edit fields
    context: Optional[str] = None  # private|executive
    size: Optional[str] = None
    notes: Optional[str] = None

    image_main_base64: str = Field(..., description="Base64 or data URL")
    image_ext: Optional[str] = Field(None, description="jpg|png|webp etc; server stores main.jpg")


class ItemUpdateRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    color_primary: Optional[str] = None
    color_variant: Optional[str] = None
    material_main: Optional[str] = None
    fit: Optional[str] = None
    collar: Optional[str] = None
    price: Optional[str] = None
    vision_description: Optional[str] = None

    # NEW: allow manual review completion + planning/edit fields
    needs_review: Optional[int] = None
    context: Optional[str] = None
    size: Optional[str] = None
    notes: Optional[str] = None


class ItemSummary(BaseModel):
    id: int
    name: str
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str] = None
    needs_review: int = 0
    context: Optional[str] = None


class ListItemsResponse(BaseModel):
    user: str
    items: List[ItemSummary]


class ItemResponse(BaseModel):
    id: int
    user_id: str
    name: str
    brand: Optional[str]
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str] = None
    needs_review: int = 0
    material_main: Optional[str]
    fit: Optional[str]
    collar: Optional[str]
    price: Optional[str]
    vision_description: Optional[str]
    image_path: Optional[str]
    created_at: str

    # NEW
    context: Optional[str] = None
    size: Optional[str] = None
    notes: Optional[str] = None

    main_image_url: Optional[str] = None
    image_urls: List[str] = []


class DeleteResponse(BaseModel):
    deleted: bool
    id: int
    image_path: str


class ReviewItem(BaseModel):
    id: int
    name: str
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str]
    needs_review: int
    suggestions: List[str] = []


class ReviewQueueResponse(BaseModel):
    user: str
    total: int
    items: List[ReviewItem]


# -------------------------
# Endpoints
# -------------------------

@router.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


def _row_to_item(row: sqlite3.Row, base_url: str) -> ItemResponse:
    image_path = row["image_path"] if "image_path" in row.keys() else None
    urls: List[str] = []
    main_url = None
    if image_path:
        main_url = f"{base_url}/images/{image_path}/main.jpg"
        urls = [main_url]
    return ItemResponse(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        brand=row["brand"],
        category=row["category"],
        color_primary=row["color_primary"],
        color_variant=row["color_variant"] if "color_variant" in row.keys() else None,
        needs_review=int(row["needs_review"]) if "needs_review" in row.keys() and row["needs_review"] is not None else 0,
        material_main=row["material_main"],
        fit=row["fit"],
        collar=row["collar"],
        price=row["price"],
        vision_description=row["vision_description"],
        image_path=image_path,
        created_at=row["created_at"],
        context=row["context"] if "context" in row.keys() else None,
        size=row["size"] if "size" in row.keys() else None,
        notes=row["notes"] if "notes" in row.keys() else None,
        main_image_url=main_url,
        image_urls=urls,
    )


@router.get("/items", response_model=ListItemsResponse, dependencies=[Depends(require_api_key)])
def list_items(request: Request, user: str) -> ListItemsResponse:
    rid = _request_id(request)
    if user not in VALID_USERS:
        _raise(400, rid, "InvalidUser", field="user", value=user)

    try:
        conn = db_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, category, color_primary, color_variant, needs_review, context
            FROM items
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user,),
        )
        rows = cur.fetchall()
    except Exception as e:
        _handle_db_exc(e, rid, op="items.list", default_error="ListFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    items = [
        ItemSummary(
            id=r["id"],
            name=r["name"],
            category=r["category"],
            color_primary=r["color_primary"],
            color_variant=r["color_variant"],
            needs_review=int(r["needs_review"] or 0),
            context=r["context"],
        )
        for r in rows
    ]
    return ListItemsResponse(user=user, items=items)


@router.get("/items/review", response_model=ReviewQueueResponse, dependencies=[Depends(require_api_key)])
def review_queue(
    request: Request,
    user: str,
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ReviewQueueResponse:
    rid = _request_id(request)
    if user not in VALID_USERS:
        _raise(400, rid, "InvalidUser", field="user", value=user)

    try:
        conn = db_conn()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS cnt FROM items WHERE user_id = ? AND needs_review = 1", (user,))
        total = int(cur.fetchone()["cnt"])

        cur.execute(
            """
            SELECT id, name, category, color_primary, color_variant, needs_review
            FROM items
            WHERE user_id = ? AND needs_review = 1
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (user, limit, offset),
        )
        rows = cur.fetchall()
    except Exception as e:
        _handle_db_exc(e, rid, op="items.review_queue", default_error="ReviewQueueFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    items: List[ReviewItem] = []
    for r in rows:
        variant = r["color_variant"]
        suggestions: List[str] = []
        if ONTOLOGY is not None and variant:
            try:
                nr = ONTOLOGY.normalize_field("color_primary", variant)
                suggestions = [s.canonical for s in (nr.suggestions or [])]
            except Exception:
                logger.exception(
                    "Ontology suggestion failed",
                    extra={"request_id": rid, "event": "ontology.suggest_failed", "value": variant},
                )
        items.append(
            ReviewItem(
                id=r["id"],
                name=r["name"],
                category=r["category"],
                color_primary=r["color_primary"],
                color_variant=variant,
                needs_review=int(r["needs_review"] or 0),
                suggestions=suggestions,
            )
        )

    return ReviewQueueResponse(user=user, total=total, items=items)


@router.get("/items/{item_id}", response_model=ItemResponse, dependencies=[Depends(require_api_key)])
def get_item(request: Request, item_id: int) -> ItemResponse:
    rid = _request_id(request)
    try:
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
    except Exception as e:
        _handle_db_exc(e, rid, op="items.get", default_error="GetFailed")
        raise
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass

    if not row:
        _raise(404, rid, "NotFound", item_id=item_id)

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.post("/items", response_model=ItemResponse, dependencies=[Depends(require_api_key)])
def create_item(request: Request, payload: ItemCreateRequest) -> ItemResponse:
    rid = _request_id(request)
    _require_valid_user(payload.user_id, rid)

    ctx = _validate_context(payload.context, rid)

    raw_color = payload.color_primary
    canonical_color, _ = _ontology_apply("color_primary", raw_color, rid)
    derived_variant, derived_review = _derive_color_variant_and_review(raw_color, canonical_color, payload.color_variant)

    canonical_category = None
    if payload.category:
        canonical_category, _ = _ontology_apply("category", payload.category, rid)

    canonical_material = None
    if payload.material_main:
        canonical_material, _ = _ontology_apply("material_main", payload.material_main, rid)

    canonical_fit = None
    if payload.fit:
        canonical_fit, _ = _ontology_apply("fit", payload.fit, rid)

    canonical_collar = None
    if payload.collar:
        canonical_collar, _ = _ontology_apply("collar", payload.collar, rid)

    create_plan = build_create_item_plan(
        payload.model_dump(),
        extra_data={
            "category": canonical_category,
            "color_primary": canonical_color,
            "color_variant": derived_variant,
            "needs_review": derived_review,
            "material_main": canonical_material,
            "fit": canonical_fit,
            "collar": canonical_collar,
            "context": ctx,
        },
        shape=API_V2_ITEM_MUTATION_SHAPE,
    )
    if not create_plan.is_valid:
        _raise(400, rid, "InvalidPayload", fields=list(create_plan.missing_required))

    logger.info(
        "Create normalization",
        extra={
            "request_id": rid,
            "event": "item.create.normalize",
            "color_primary": canonical_color,
            "color_variant": derived_variant,
            "needs_review": derived_review,
            "context": ctx,
        },
    )

    try:
        raw_bytes = _decode_image_base64(payload.image_main_base64)
    except Exception:
        logger.exception("Image base64 decode failed", extra={"request_id": rid, "event": "item.create.image_decode"})
        _raise(400, rid, "ImageDecodeFailed", stage="base64")

    if len(raw_bytes) > settings.MAX_IMAGE_BYTES:
        _raise(413, rid, "ImageTooLarge", stage="image", max_bytes=settings.MAX_IMAGE_BYTES)

    try:
        jpg_bytes = _normalize_image_to_jpg(raw_bytes)
    except Exception:
        logger.exception("Image normalize failed", extra={"request_id": rid, "event": "item.create.image_normalize"})
        _raise(400, rid, "ImageDecodeFailed", stage="image")

    conn = db_conn()
    cur = conn.cursor()

    item_id: Optional[int] = None
    created_image = None

    try:
        cur.execute(
            f"INSERT INTO items ({create_plan.insert_columns_sql()}) VALUES ({create_plan.insert_placeholders_sql()})",
            create_plan.ordered_params(),
        )
        item_id = int(cur.lastrowid)

        created_image = create_image_folder_for_item(settings.IMG_DIR, payload.user_id, payload.name, item_id, jpg_bytes)

        cur.execute("UPDATE items SET image_path = ? WHERE id = ?", (created_image.rel_path, item_id))
        conn.commit()

        logger.info(
            "Create OK",
            extra={
                "request_id": rid,
                "event": "item.create.ok",
                "item_id": item_id,
                "image_path": created_image.rel_path,
            },
        )

    except Exception as e:
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
            logger.exception("Create cleanup failed", extra={"request_id": rid, "event": "item.create.cleanup"})

        if _is_db_locked(e):
            _raise(503, rid, "DbLocked", stage="db", op="items.create")

        logger.exception("Create failed", extra={"request_id": rid, "event": "item.create.failed"})
        _raise(500, rid, "CreateFailed", stage="db", op="items.create")

    finally:
        conn.close()

    try:
        conn2 = db_conn()
        cur2 = conn2.cursor()
        cur2.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur2.fetchone()
        conn2.close()
    except Exception as e:
        _handle_db_exc(e, rid, op="items.create.fetch", default_error="CreateFailed")
        raise

    if not row:
        _raise(500, rid, "CreateFailed", stage="db", reason="missing_row_after_create")

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.post("/items/validate", dependencies=[Depends(require_api_key)])
def validate_item(request: Request, payload: ItemCreateRequest) -> Dict[str, Any]:
    rid = _request_id(request)
    _require_valid_user(payload.user_id, rid)

    ctx = _validate_context(payload.context, rid)

    raw_color = payload.color_primary
    canonical_color, _ = _ontology_apply("color_primary", raw_color, rid)
    derived_variant, derived_review = _derive_color_variant_and_review(raw_color, canonical_color, payload.color_variant)

    canonical_category = None
    if payload.category:
        canonical_category, _ = _ontology_apply("category", payload.category, rid)

    canonical_material = None
    if payload.material_main:
        canonical_material, _ = _ontology_apply("material_main", payload.material_main, rid)

    canonical_fit = None
    if payload.fit:
        canonical_fit, _ = _ontology_apply("fit", payload.fit, rid)

    canonical_collar = None
    if payload.collar:
        canonical_collar, _ = _ontology_apply("collar", payload.collar, rid)

    try:
        raw_bytes = _decode_image_base64(payload.image_main_base64)
    except Exception:
        logger.exception("Validate image base64 decode failed", extra={"request_id": rid, "event": "item.validate.image_decode"})
        _raise(400, rid, "ImageDecodeFailed", stage="base64")

    if len(raw_bytes) > settings.MAX_IMAGE_BYTES:
        _raise(413, rid, "ImageTooLarge", stage="image", max_bytes=settings.MAX_IMAGE_BYTES)

    try:
        jpg_bytes = _normalize_image_to_jpg(raw_bytes)
    except Exception:
        logger.exception("Validate image normalize failed", extra={"request_id": rid, "event": "item.validate.image_normalize"})
        _raise(400, rid, "ImageDecodeFailed", stage="image")

    width = None
    height = None
    try:
        with Image.open(io.BytesIO(jpg_bytes)) as im2:
            width, height = im2.size
    except Exception:
        pass

    slug = _slugify(payload.name)
    example_rel = str(Path(payload.user_id) / f"{slug}_NEW").replace("\\", "/")

    return {
        "ok": True,
        "request_id": rid,
        "example_image_path": example_rel,
        "normalized_fields": {
            "user_id": payload.user_id,
            "name": payload.name,
            "brand": payload.brand,
            "category": canonical_category,
            "color_primary": canonical_color,
            "color_variant": derived_variant,
            "needs_review": int(derived_review),
            "material_main": canonical_material,
            "fit": canonical_fit,
            "collar": canonical_collar,
            "price": payload.price,
            "vision_description": payload.vision_description,
            "context": ctx,
            "size": payload.size,
            "notes": payload.notes,
        },
        "normalized_image": {
            "stored_ext": "jpg",
            "bytes": len(jpg_bytes),
            "width": width,
            "height": height,
            "max_dim": settings.IMAGE_MAX_DIM,
        },
    }


@router.patch("/items/{item_id}", response_model=ItemResponse, dependencies=[Depends(require_api_key)])
def update_item(request: Request, item_id: int, payload: ItemUpdateRequest) -> ItemResponse:
    rid = _request_id(request)

    conn = db_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        existing = cur.fetchone()
    except Exception as e:
        conn.close()
        _handle_db_exc(e, rid, op="items.update.load", default_error="UpdateFailed")
        raise

    if not existing:
        conn.close()
        _raise(404, rid, "NotFound", item_id=item_id)

    updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
    if not updates:
        conn.close()
        _raise(400, rid, "NoFields")

    if "context" in updates:
        updates["context"] = _validate_context(updates.get("context"), rid)

    if "needs_review" in updates and updates["needs_review"] is not None:
        updates["needs_review"] = int(updates["needs_review"])

    if "color_primary" in updates:
        raw_color = updates.get("color_primary")
        explicit_variant = updates.get("color_variant")
        canonical_color, _ = _ontology_apply("color_primary", raw_color, rid)
        updates["color_primary"] = canonical_color
        derived_variant, derived_review = _derive_color_variant_and_review(raw_color, canonical_color, explicit_variant)

        if "color_variant" not in updates:
            updates["color_variant"] = derived_variant
        if "needs_review" not in updates:
            updates["needs_review"] = derived_review

        logger.info(
            "Update color",
            extra={
                "request_id": rid,
                "event": "item.update.color",
                "item_id": item_id,
                "color_primary": canonical_color,
                "color_variant": updates.get("color_variant"),
                "needs_review": updates.get("needs_review"),
            },
        )

    if "category" in updates and updates["category"] is not None:
        updates["category"], _ = _ontology_apply("category", updates["category"], rid)
    if "material_main" in updates and updates["material_main"] is not None:
        updates["material_main"], _ = _ontology_apply("material_main", updates["material_main"], rid)
    if "fit" in updates and updates["fit"] is not None:
        updates["fit"], _ = _ontology_apply("fit", updates["fit"], rid)
    if "collar" in updates and updates["collar"] is not None:
        updates["collar"], _ = _ontology_apply("collar", updates["collar"], rid)

    old_rel = existing["image_path"]
    move_result = None

    if old_rel and ("name" in updates or "user_id" in updates):
        old_user = existing["user_id"]
        old_name = existing["name"]
        old_id = existing["id"]

        new_user = updates.get("user_id", old_user)
        new_name = updates.get("name", old_name)
        if new_user not in VALID_USERS:
            conn.close()
            _raise(400, rid, "InvalidUser", field="user_id", value=new_user)

        try:
            move_result = move_image_folder_for_item(settings.IMG_DIR, old_rel, new_user, new_name, old_id)
            if move_result.conflict:
                logger.warning(
                    "Folder move skipped (destination exists)",
                    extra={"request_id": rid, "event": "item.update.move_skipped", "src": old_rel, "dst": move_result.new_rel},
                )
            elif move_result.moved:
                updates["image_path"] = move_result.new_rel
                logger.info(
                    "Moved image folder",
                    extra={"request_id": rid, "event": "item.update.move_ok", "src": old_rel, "dst": move_result.new_rel, "item_id": item_id},
                )
        except Exception:
            logger.exception(
                "Folder move failed (continuing metadata update)",
                extra={"request_id": rid, "event": "item.update.move_failed", "item_id": item_id},
            )
            updates.pop("image_path", None)
            move_result = None

    update_plan = build_update_item_plan(updates, shape=API_V2_ITEM_MUTATION_SHAPE, immutable_fields=())
    try:
        require_non_empty_update(update_plan)
    except ValueError:
        conn.close()
        _raise(400, rid, "NoValidFields")

    sql = f"UPDATE items SET {update_plan.update_assignment_sql()} WHERE id = ?"
    params = [*update_plan.ordered_params(), item_id]

    try:
        cur.execute(sql, params)
        conn.commit()
        logger.info("Update OK", extra={"request_id": rid, "event": "item.update.ok", "item_id": item_id})
    except Exception as e:
        conn.rollback()

        if move_result and move_result.moved:
            try:
                rollback_moved_image_dir(move_result)
                logger.warning(
                    "Rolled back folder move after DB failure",
                    extra={"request_id": rid, "event": "item.update.move_rollback", "item_id": item_id},
                )
            except Exception:
                logger.exception(
                    "Rollback of folder move failed",
                    extra={"request_id": rid, "event": "item.update.move_rollback_failed", "item_id": item_id},
                )

        if _is_db_locked(e):
            _raise(503, rid, "DbLocked", stage="db", op="items.update")

        logger.exception("Update failed", extra={"request_id": rid, "event": "item.update.failed", "item_id": item_id})
        _raise(500, rid, "UpdateFailed", stage="db", op="items.update")
    finally:
        conn.close()

    try:
        conn2 = db_conn()
        cur2 = conn2.cursor()
        cur2.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur2.fetchone()
        conn2.close()
    except Exception as e:
        _handle_db_exc(e, rid, op="items.update.fetch", default_error="UpdateFailed")
        raise

    if not row:
        _raise(500, rid, "UpdateFailed", stage="db", reason="missing_row_after_update")

    base_url = str(request.base_url).rstrip("/")
    return _row_to_item(row, base_url)


@router.delete("/items/{item_id}", response_model=DeleteResponse, dependencies=[Depends(require_api_key)])
def delete_item(request: Request, item_id: int) -> DeleteResponse:
    rid = _request_id(request)

    conn = db_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, image_path FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
    except Exception as e:
        conn.close()
        _handle_db_exc(e, rid, op="items.delete.load", default_error="DeleteFailed")
        raise

    if not row:
        conn.close()
        _raise(404, rid, "NotFound", item_id=item_id)

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
            except RuntimeError as e:
                if str(e) == "JailCheckFailed":
                    _raise(400, rid, "JailCheckFailed", stage="fs", op="items.delete")
                raise

        cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()

        logger.info(
            "Delete OK",
            extra={"request_id": rid, "event": "item.delete.ok", "item_id": item_id, "image_path": image_path},
        )

    except HTTPException:
        if trash_result and trash_result.moved:
            try:
                rollback_trashed_image_dir(trash_result)
            except Exception:
                logger.exception(
                    "Rollback move failed after HTTPException",
                    extra={"request_id": rid, "event": "item.delete.rollback_failed"},
                )
        raise
    except Exception as e:
        conn.rollback()
        if trash_result and trash_result.moved:
            try:
                rollback_trashed_image_dir(trash_result)
            except Exception:
                logger.exception(
                    "Rollback move failed after DeleteFailed",
                    extra={"request_id": rid, "event": "item.delete.rollback_failed"},
                )

        if _is_db_locked(e):
            _raise(503, rid, "DbLocked", stage="db", op="items.delete")

        logger.exception("Delete failed", extra={"request_id": rid, "event": "item.delete.failed", "item_id": item_id})
        _raise(500, rid, "DeleteFailed", stage="db", op="items.delete")
    finally:
        conn.close()

    if trash_result and trash_result.moved:
        try:
            cleanup_trashed_image_dir(trash_result)
        except Exception:
            logger.exception(
                "Trash cleanup failed (best effort)",
                extra={"request_id": rid, "event": "item.delete.trash_cleanup_failed"},
            )

    return DeleteResponse(deleted=True, id=item_id, image_path=image_path)

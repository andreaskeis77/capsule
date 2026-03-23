from __future__ import annotations

import base64
import io
import logging
import os
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import Header, HTTPException, Request
from PIL import Image

from src import settings
from src.api_v2_contracts import VALID_CONTEXTS, VALID_USERS
from src.error_contract import error_class_for_status
from src.ontology_runtime import NormalizationResult, OntologyManager

logger = logging.getLogger("WardrobeControl")

ONTOLOGY: Optional[OntologyManager] = None


def _request_id(request: Request) -> str:
    return request.state.request_id if hasattr(request.state, "request_id") else "-"


def _detail(status_code: int, request_id: str, error: str, **extra: Any) -> Dict[str, Any]:
    detail: Dict[str, Any] = {
        "error": error,
        "request_id": request_id,
        "error_class": error_class_for_status(status_code),
    }
    detail.update(extra)
    return detail


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
    normalized = value.strip().lower()
    return normalized or None


def _validate_context(value: Optional[str], rid: str) -> Optional[str]:
    normalized = _normalize_context(value)
    if normalized is None:
        return None
    if normalized not in VALID_CONTEXTS:
        _raise(
            400,
            rid,
            "InvalidContext",
            field="context",
            value=value,
            allowed=sorted(list(VALID_CONTEXTS)),
        )
    return normalized


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
    except Exception as exc:
        ONTOLOGY = None
        logger.warning(
            f"Ontology init failed; continuing without ontology. Error: {exc}",
            extra={"request_id": "-", "event": "ontology.init_failed"},
            exc_info=True,
        )


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
    value = name.strip().lower()
    value = (
        value.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("Ã¤", "ae")
        .replace("Ã¶", "oe")
        .replace("Ã¼", "ue")
        .replace("ÃŸ", "ss")
    )
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "item"


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

    value = data.strip()
    if value.startswith("data:"):
        comma = value.find(",")
        if comma == -1:
            raise ValueError("Invalid data URL")
        value = value[comma + 1 :]
    return base64.b64decode(value, validate=False)


def _normalize_image_to_jpg(raw: bytes) -> bytes:
    with Image.open(io.BytesIO(raw)) as img:
        img = img.convert("RGB")
        img.thumbnail((settings.IMAGE_MAX_DIM, settings.IMAGE_MAX_DIM))
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=settings.IMAGE_JPEG_QUALITY, optimize=True)
        return out.getvalue()


def _rmtree_robust(path: Path | str, ignore_errors: bool = False) -> None:
    path = Path(path)

    import inspect
    import stat
    import time

    has_onexc = "onexc" in inspect.signature(shutil.rmtree).parameters

    def _make_writable(p: str | os.PathLike[str]) -> None:
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


def _ontology_apply(field: str, value: Optional[str], request_id: str) -> Tuple[Optional[str], NormalizationResult]:
    if ONTOLOGY is None:
        result = NormalizationResult(
            field=field,
            original=value or "",
            canonical=value,
            matched_by="none",
            confidence=0.0,
            suggestions=[],
            meta=None,
        )
        return value, result

    canonical, result = ONTOLOGY.validate_or_normalize(field, value)
    if settings.ONTOLOGY_MODE == "soft" and canonical is None and field in settings.ONTOLOGY_TOLERANT_FIELDS:
        logger.info(
            "Ontology tolerant miss",
            extra={"request_id": request_id, "event": "ontology.tolerant_miss", "field": field, "value": value},
        )
        return None, result

    if settings.ONTOLOGY_MODE in {"soft", "strict"} and canonical is None:
        detail = _detail(
            400,
            request_id,
            "OntologyValidationError",
            field=field,
            value=value,
            suggestions=[
                {"canonical": suggestion.canonical, "score": suggestion.score, "label": suggestion.label}
                for suggestion in (result.suggestions or [])
            ],
        )
        raise HTTPException(status_code=400, detail=detail)

    return canonical, result


def _derive_color_variant_and_review(
    raw_color: Optional[str],
    canonical_color: Optional[str],
    explicit_variant: Optional[str],
) -> Tuple[Optional[str], int]:
    raw = (raw_color or "").strip()
    canon = (canonical_color or "").strip()

    if explicit_variant is not None:
        variant = explicit_variant.strip() or None
        needs_review = 1 if (raw and canon and raw.lower() != canon.lower()) else 0
        return variant, needs_review

    if raw and canon and raw.lower() != canon.lower():
        return raw, 1

    return None, 0

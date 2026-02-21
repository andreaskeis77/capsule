# FILE: src/error_contract.py
from __future__ import annotations

from typing import Any, Dict, List


def error_code_for_status(status_code: int) -> str:
    """
    Stable error codes (string) derived from HTTP status when a handler/endpoint
    did not provide a specific code.
    """
    mapping = {
        400: "BadRequest",
        401: "Unauthorized",
        403: "Forbidden",
        404: "NotFound",
        405: "MethodNotAllowed",
        409: "Conflict",
        413: "PayloadTooLarge",
        422: "ValidationError",
        429: "RateLimited",
    }
    if status_code in mapping:
        return mapping[status_code]
    if status_code >= 500:
        return "ServerError"
    return "HttpError"


def error_class_for_status(status_code: int) -> str:
    """
    Failure taxonomy (very small first step):
      - permanent: caller must change request/data
      - transient: retry may succeed
    """
    if status_code >= 500:
        return "transient"
    if status_code in (408, 429):
        return "transient"
    return "permanent"


def normalize_detail(detail: Any, status_code: int, request_id: str) -> Dict[str, Any]:
    """
    Ensure FastAPI error responses always have a dict detail with at least:
      - error
      - request_id
      - error_class
    """
    out: Dict[str, Any] = {}

    if isinstance(detail, dict):
        out.update(detail)
    elif detail is None:
        pass
    else:
        out["message"] = str(detail)

    out.setdefault("error", error_code_for_status(status_code))
    out.setdefault("request_id", request_id)
    out.setdefault("error_class", error_class_for_status(status_code))
    return out


def validation_detail(errors: List[Dict[str, Any]], request_id: str) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    for e in errors:
        loc = e.get("loc", [])
        if isinstance(loc, tuple):
            loc = list(loc)
        issues.append(
            {
                "loc": loc,
                "msg": e.get("msg"),
                "type": e.get("type"),
            }
        )

    return {
        "error": "ValidationError",
        "request_id": request_id,
        "error_class": "permanent",
        "issues": issues,
    }
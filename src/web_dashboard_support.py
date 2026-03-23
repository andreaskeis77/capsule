from __future__ import annotations

import html as html_lib
import json
import sqlite3
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from flask import abort, make_response, request, send_from_directory

from src import settings
from src.db_schema import ensure_schema


# Ensure DB schema exists (best-effort; tests rely on ensure_schema)
ensure_schema()


def ensure_db_ready() -> None:
    # Reload settings so env overrides (tests) are honored.
    try:
        settings.reload_settings()
    except Exception:
        pass
    try:
        ensure_schema()
    except Exception:
        pass


def get_db_connection() -> sqlite3.Connection:
    # Read from settings dynamically (supports settings.reload_settings())
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def serve_image_file(filename: str):
    return send_from_directory(str(settings.IMG_DIR), urllib.parse.unquote(filename))


def safe_str(value: Optional[str]) -> str:
    return (value or "").strip()


def parse_ids_param(raw: Optional[str], limit: int = 500) -> List[int]:
    """Parse ?ids=101,102,... into an ordered unique list of positive ints."""
    if not raw:
        return []
    raw = raw.strip()
    if not raw:
        return []

    parts = [part.strip() for part in raw.split(",")]
    out: List[int] = []
    seen: set[int] = set()
    for part in parts:
        if not part:
            continue
        try:
            number = int(part)
        except ValueError:
            continue
        if number <= 0 or number in seen:
            continue
        seen.add(number)
        out.append(number)
        if len(out) >= limit:
            break
    return out


def load_images_for_item(image_path: Optional[str]) -> List[str]:
    """Return stable image URLs relative to /images/... for one image folder."""
    rel = safe_str(image_path)
    if not rel:
        return []
    abs_dir = settings.IMG_DIR / Path(rel)
    if not abs_dir.is_dir():
        return []

    files: List[str] = []
    try:
        for path in abs_dir.iterdir():
            if path.is_file() and path.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                files.append(path.name)
    except Exception:
        return []

    files.sort(key=lambda name: (0 if name.lower().startswith("main") else 1, name.lower()))
    return [
        f"/images/{urllib.parse.quote(rel)}/{urllib.parse.quote(filename)}"
        for filename in files
    ]


def is_local_request() -> bool:
    ip = (request.remote_addr or "").strip()
    return ip in ("127.0.0.1", "::1")


def require_admin_local() -> None:
    if not is_local_request():
        abort(403, description="Admin mode is only available locally (127.0.0.1).")


def api_base_url() -> str:
    return request.host_url.rstrip("/")


def api_key() -> str:
    key = (settings.API_KEY or "").strip()
    if not key:
        abort(500, description="WARDROBE_API_KEY is not set in environment.")
    return key


def api_headers() -> Dict[str, str]:
    return {"X-API-Key": api_key(), "Accept": "application/json"}


def allow_local_noauth() -> bool:
    return bool(getattr(settings, "ALLOW_LOCAL_NOAUTH", False))


def require_api_key() -> None:
    """Require X-API-Key for remote calls (legacy /api/v1 endpoints)."""
    if allow_local_noauth() and is_local_request():
        return
    provided = (request.headers.get("X-API-Key") or "").strip()
    if not provided or provided != api_key():
        abort(401, description="Unauthorized: missing/invalid X-API-Key")


def http_request(method: str, url: str, json_body: Optional[Dict[str, Any]] = None) -> Tuple[int, str]:
    """Minimal stdlib HTTP client that preserves HTTP error status and body."""
    import urllib.error
    import urllib.request

    data = None
    headers = api_headers().copy()
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read() or b""
            try:
                body = raw.decode("utf-8", errors="replace")
            except Exception:
                body = str(raw)
            return int(resp.getcode()), body
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read() or b""
        except Exception:
            raw = b""
        try:
            body = raw.decode("utf-8", errors="replace")
        except Exception:
            body = str(raw)
        status = int(getattr(exc, "code", 0) or 0)
        if not body:
            body = str(exc)
        return status, body
    except urllib.error.URLError as exc:
        return 0, f"URLError: {getattr(exc, 'reason', exc)}"
    except Exception as exc:
        return 0, str(exc)


def pretty_json(text: str) -> Optional[str]:
    t = (text or "").strip()
    if not t:
        return None
    if not (t.startswith("{") or t.startswith("[")):
        return None
    try:
        obj = json.loads(t)
        return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
    except Exception:
        return None


def admin_api_error_response(action: str, status: int, url: str, body: str, user: str):
    """Return a readable HTML error page for admin actions."""
    http_status = status if 400 <= status <= 599 else 502
    pretty = pretty_json(body) or (body or "").strip() or "(no body)"
    if len(pretty) > 12000:
        pretty = pretty[:12000] + "\n…(truncated)…"

    back_url = f"/?user={urllib.parse.quote(user)}&mode=admin"
    html = f"""
    <h1>Admin API Error</h1>
    <p><strong>Admin-Speichern fehlgeschlagen</strong></p>
    <p>action: {html_lib.escape(action)}<br>status: {http_status}</p>
    <p><strong>URL:</strong> {html_lib.escape(url)}</p>
    <h3>API Response</h3>
    <pre>{html_lib.escape(pretty)}</pre>
    <p><a href=\"{back_url}\">← Zur Admin-Übersicht</a></p>
    """
    return make_response(html, http_status)


def build_admin_patch_payload(form: Mapping[str, Any]) -> Dict[str, object]:
    editable_fields = [
        "name",
        "category",
        "brand",
        "color_primary",
        "color_variant",
        "material_main",
        "fit",
        "collar",
        "price",
        "needs_review",
        "context",
        "size",
        "notes",
    ]

    payload: Dict[str, object] = {}
    for field in editable_fields:
        if field not in form:
            continue
        value = form.get(field, "")
        if field == "needs_review":
            payload[field] = True if value in ("1", "true", "on", "yes") else False
        else:
            payload[field] = str(value).strip()

    # keep old behavior: do not send empty strings (no clearing via admin form)
    return {key: value for key, value in payload.items() if not (isinstance(value, str) and value == "")}


__all__ = [
    "admin_api_error_response",
    "allow_local_noauth",
    "api_base_url",
    "api_headers",
    "api_key",
    "build_admin_patch_payload",
    "ensure_db_ready",
    "get_db_connection",
    "http_request",
    "is_local_request",
    "load_images_for_item",
    "parse_ids_param",
    "pretty_json",
    "require_admin_local",
    "require_api_key",
    "safe_str",
    "serve_image_file",
]

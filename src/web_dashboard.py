from __future__ import annotations

import html as html_lib
import json
import logging
import sqlite3
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
)

from src import settings
from src import category_map as cm
from src.dashboard_category_view import build_dashboard_category_view
from src.dashboard_request_state import parse_dashboard_request_state
from src.db_schema import ensure_schema

# Ensure DB schema exists (best-effort; tests rely on ensure_schema)
ensure_schema()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WardrobeAPI")

BASE_DIR = settings.BASE_DIR  # repo root as Path
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
flask_app = app


def _ensure_db_ready() -> None:
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


@app.route("/images/<path:filename>")
def serve_images(filename: str):
    return send_from_directory(str(settings.IMG_DIR), urllib.parse.unquote(filename))


def _safe_str(x: Optional[str]) -> str:
    return (x or "").strip()


def _parse_ids_param(raw: Optional[str], limit: int = 500) -> List[int]:
    """
    Parse ?ids=101,102,... into an ordered list of unique ints (stable order).
    Invalid tokens are ignored. Enforces a hard limit to avoid abuse.
    """
    if not raw:
        return []
    raw = raw.strip()
    if not raw:
        return []

    parts = [p.strip() for p in raw.split(",")]
    out: List[int] = []
    seen = set()
    for p in parts:
        if not p:
            continue
        try:
            n = int(p)
        except ValueError:
            continue
        if n <= 0:
            continue
        if n in seen:
            continue
        seen.add(n)
        out.append(n)
        if len(out) >= limit:
            break
    return out


def _load_images_for_item(image_path: Optional[str]) -> List[str]:
    """
    Returns list of image URLs (relative to /images/...).
    """
    rel = _safe_str(image_path)
    if not rel:
        return []
    abs_dir = settings.IMG_DIR / Path(rel)
    if not abs_dir.is_dir():
        return []

    files: List[str] = []
    try:
        for p in abs_dir.iterdir():
            if p.is_file() and p.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                files.append(p.name)
    except Exception:
        return []

    # stable order: main first, then others
    files.sort(key=lambda x: (0 if x.lower().startswith("main") else 1, x.lower()))
    return [
        f"/images/{urllib.parse.quote(rel)}/{urllib.parse.quote(fn)}"
        for fn in files
    ]


def _is_local_request() -> bool:
    ip = (request.remote_addr or "").strip()
    return ip in ("127.0.0.1", "::1")


def _require_admin_local() -> None:
    if not _is_local_request():
        abort(403, description="Admin mode is only available locally (127.0.0.1).")


def _api_base_url() -> str:
    return request.host_url.rstrip("/")


def _api_key() -> str:
    key = (settings.API_KEY or "").strip()
    if not key:
        abort(500, description="WARDROBE_API_KEY is not set in environment.")
    return key


def _api_headers() -> Dict[str, str]:
    return {"X-API-Key": _api_key(), "Accept": "application/json"}


def _allow_local_noauth() -> bool:
    return bool(getattr(settings, "ALLOW_LOCAL_NOAUTH", False))


def _require_api_key() -> None:
    """
    Require X-API-Key for remote calls (legacy /api/v1 endpoints).
    """
    if _allow_local_noauth() and _is_local_request():
        return
    provided = (request.headers.get("X-API-Key") or "").strip()
    if not provided or provided != _api_key():
        abort(401, description="Unauthorized: missing/invalid X-API-Key")


def _http_request(method: str, url: str, json_body: Optional[Dict] = None) -> Tuple[int, str]:
    """
    Minimal HTTP client (stdlib) for calling our own API v2 from admin routes.
    Returns (status_code, body_text).

    IMPORTANT: preserves HTTPError status + response body.
    """
    import urllib.error
    import urllib.request

    data = None
    headers = _api_headers().copy()
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
    except urllib.error.HTTPError as e:
        # Preserve status + read body (this was previously swallowed -> status 0)
        try:
            raw = e.read() or b""
        except Exception:
            raw = b""
        try:
            body = raw.decode("utf-8", errors="replace")
        except Exception:
            body = str(raw)
        status = int(getattr(e, "code", 0) or 0)
        if not body:
            body = str(e)
        return status, body
    except urllib.error.URLError as e:
        return 0, f"URLError: {getattr(e, 'reason', e)}"
    except Exception as e:
        return 0, str(e)


def _pretty_json(text: str) -> Optional[str]:
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


def _admin_api_error_response(action: str, status: int, url: str, body: str, user: str):
    """
    Return a readable HTML error page for admin actions.
    Shows the real API response (pretty JSON if possible).
    """
    http_status = status if 400 <= status <= 599 else 502
    pretty = _pretty_json(body) or (body or "").strip() or "(no body)"

    # avoid huge pages
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


def _decorate_item(item: Dict[str, object]) -> Dict[str, object]:
    raw_cat = item.get("category")
    name = item.get("name")
    internal = cm.infer_internal_category(raw_cat, name=name)
    item["category_key"] = internal
    item["category_label"] = cm.display_category_label(raw_cat, name=name)
    item["category_group"] = cm.category_group_for_internal(internal)
    item["category_raw"] = (raw_cat or "").strip() if raw_cat is not None else ""
    item["category_is_unknown"] = bool(item["category_raw"]) and internal is None
    item["category_mapped_from_raw"] = bool(item["category_raw"]) and (internal is not None) and (item["category_raw"] != internal)
    item["all_images"] = _load_images_for_item(item.get("image_path"))
    item["primary_image"] = item["all_images"][0] if item["all_images"] else None
    return item


@app.route("/")
def index():
    """
    Dashboard:
    - default user is karen (query param)
    - category filters (new taxonomy)
    - optional selection mode (?mode=select&ids=1,2,3)
    - admin mode (?mode=admin) is local-only
    """
    state = parse_dashboard_request_state(
        request.args,
        parse_ids_param=_parse_ids_param,
        normalize_filter_key=cm.normalize_filter_key,
    )
    if state.admin_mode:
        _require_admin_local()

    conn = get_db_connection()
    rows_base = conn.execute(
        """
        SELECT id, user_id, name, brand, category, color_primary, color_variant,
               needs_review, context, size, notes, image_path
        FROM items
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (state.user,),
    ).fetchall()
    conn.close()

    items_all: List[Dict[str, object]] = []
    for r in rows_base:
        items_all.append(_decorate_item(dict(r)))

    category_view = build_dashboard_category_view(
        items_all,
        ctx=state.ctx,
        review_only=state.review_only,
        active_cat=state.active_cat,
    )

    ids_param = ",".join(str(i) for i in state.selected_ids) if state.selection_mode else ""

    return render_template(
        "index.html",
        user_id=state.user,
        items=category_view.items,
        active_cat=category_view.active_cat,
        active_cat_label=category_view.active_cat_label,
        quick_filters=category_view.quick_filters,
        filter_dropdown_groups=category_view.filter_dropdown_groups,
        total_count=len(category_view.items_base),
        shown_count=len(category_view.items),
        base_count=len(items_all),
        active_ctx=state.ctx,
        review_only=state.review_only,
        selection_mode=state.selection_mode,
        selected_ids=state.selected_ids,
        ids_param=ids_param,
        admin_mode=state.admin_mode,
    )


@app.route("/item/<int:item_id>")
def item_detail(item_id: int):
    """
    Detailseite für 1 Item.
    Optional ?user=karen wird nur für UI-Navigation verwendet.
    """
    user = request.args.get("user", "karen").strip().lower()

    conn = get_db_connection()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        abort(404)

    item = _decorate_item(dict(row))
    return render_template("item_detail.html", user_id=user, item=item)


# -------------------------
# ADMIN: Edit + Delete
# -------------------------

@app.route("/admin/item/<int:item_id>", methods=["GET"])
def admin_edit_item(item_id: int):
    _require_admin_local()
    user = request.args.get("user", "karen").strip().lower()

    conn = get_db_connection()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        abort(404)

    item = _decorate_item(dict(row))
    return render_template(
        "admin_item_edit.html",
        user_id=user,
        item=item,
        category_admin_groups=cm.admin_option_groups(),
        category_admin_labels=cm.ADMIN_LABEL,
    )


@app.route("/admin/item/<int:item_id>/save", methods=["POST"])
def admin_save_item(item_id: int):
    _require_admin_local()
    user = request.args.get("user", "karen").strip().lower()

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
    for f in editable_fields:
        if f in request.form:
            v = request.form.get(f, "")
            if f == "needs_review":
                payload[f] = True if v in ("1", "true", "on", "yes") else False
            else:
                payload[f] = v.strip()

    # keep old behavior: do not send empty strings (no clearing via admin form)
    payload = {k: v for k, v in payload.items() if not (isinstance(v, str) and v == "")}

    api_url = f"{_api_base_url()}/api/v2/items/{item_id}"
    status, body = _http_request("PATCH", api_url, json_body=payload)
    if status not in (200, 204):
        logger.warning(
            "Admin PATCH failed: status=%s url=%s body=%s",
            status,
            api_url,
            body[:800] if body else "",
        )
        return _admin_api_error_response("PATCH", status, api_url, body, user)
    return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")


@app.route("/admin/item/<int:item_id>/delete", methods=["POST"])
def admin_delete_item(item_id: int):
    _require_admin_local()
    user = request.args.get("user", "karen").strip().lower()

    api_url = f"{_api_base_url()}/api/v2/items/{item_id}"
    status, body = _http_request("DELETE", api_url, json_body=None)
    if status not in (200, 204):
        logger.warning(
            "Admin DELETE failed: status=%s url=%s body=%s",
            status,
            api_url,
            body[:800] if body else "",
        )
        return _admin_api_error_response("DELETE", status, api_url, body, user)
    return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")


# --- GPT API ENDPOINTS (Legacy, keep for compatibility; protected via X-API-Key) ---

@app.route("/api/v1/inventory", methods=["GET"])
def api_get_inventory():
    _require_api_key()
    user = request.args.get("user", "karen")

    try:
        settings.reload_settings()
    except Exception:
        pass

    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(items)").fetchall()}
        want = [
            "id",
            "name",
            "category",
            "color_primary",
            "color_variant",
            "needs_review",
            "context",
            "size",
            "notes",
            "image_path",
        ]
        select = []
        for col in want:
            if col in cols:
                select.append(col)
            else:
                select.append(f"NULL AS {col}")
        sql = "SELECT " + ", ".join(select) + " FROM items WHERE user_id = ?"
        rows = conn.execute(sql, (user,)).fetchall()
        items = [dict(row) for row in rows]
    finally:
        conn.close()
    return jsonify({"user": user, "items": items})


@app.route("/api/v1/item/<int:item_id>", methods=["GET"])
def api_get_item_detail(item_id: int):
    _require_api_key()
    _ensure_db_ready()
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False)

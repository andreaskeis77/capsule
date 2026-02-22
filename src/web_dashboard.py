# FILE: src/web_dashboard.py
from __future__ import annotations

import logging
import os
import sqlite3
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory

from src import settings
from src.db_schema import ensure_schema

def _ensure_db_ready():
    # Reload settings so env overrides (tests) are honored.
    try:
        settings.reload_settings()
    except Exception:
        pass
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WardrobeAPI")

BASE_DIR = settings.BASE_DIR  # repo root as Path

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
flask_app = app


def get_db_connection():
    # Read from settings dynamically (supports settings.reload_settings())
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/images/<path:filename>")
def serve_images(filename):
    # Read from settings dynamically (supports settings.reload_settings())
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


def _infer_top_category(category_value: Optional[str], name_value: Optional[str] = None) -> str:
    """
    Heuristische Zuordnung DB-category -> Oberbegriff für Karen (UI-Filter).
    DB category ist in eurem System typischerweise ein Ontologie-ID-String (z.B. cat_...),
    kann aber auch Freitext sein (legacy). Daher rein stringbasiert.
    """
    c = _safe_str(category_value).lower()
    n = _safe_str(name_value).lower()
    blob = f"{c} {n}".strip()

    # Reihenfolge ist wichtig (spezifisch -> unspezifisch)
    if any(k in blob for k in ["shoe", "footwear", "schuh", "sneaker", "boot", "stiefel", "loafer", "pumps", "sandale"]):
        return "Schuhe"
    if any(k in blob for k in ["bag", "handtasche", "clutch", "tote", "purse", "rucksack", "backpack"]):
        return "Handtaschen"
    if any(k in blob for k in ["dress", "kleid"]):
        return "Kleider"
    if any(k in blob for k in ["bluse", "shirt", "top", "pullover", "sweater", "hemd", "blazer"]):
        return "Blusen & Oberteile"
    if any(k in blob for k in ["hose", "pants", "jeans", "trouser"]):
        return "Hosen"
    if any(k in blob for k in ["rock", "skirt"]):
        return "Röcke"
    if any(k in blob for k in ["mantel", "coat", "jacke", "jacket", "parka", "trench"]):
        return "Jacken & Mäntel"
    if any(k in blob for k in ["ohrring", "kette", "armband", "ring", "brosche", "schmuck", "accessoire", "accessory"]):
        return "Accessoires"

    return "Sonstiges"


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
    return [f"/images/{urllib.parse.quote(rel)}/{urllib.parse.quote(fn)}" for fn in files]


def _is_local_request() -> bool:
    # Default safety: Admin only from localhost
    ip = (request.remote_addr or "").strip()
    return ip in ("127.0.0.1", "::1")


def _require_admin_local():
    if not _is_local_request():
        abort(403, description="Admin mode is only available locally (127.0.0.1).")


def _api_base_url() -> str:
    # same host as current request
    return request.host_url.rstrip("/")


def _api_key() -> str:
    key = (settings.API_KEY or "").strip()
    if not key:
        abort(500, description="WARDROBE_API_KEY is not set in environment.")
    return key


def _api_headers() -> Dict[str, str]:
    return {"X-API-Key": _api_key()}


def _allow_local_noauth() -> bool:
    return bool(getattr(settings, "ALLOW_LOCAL_NOAUTH", False))


def _require_api_key() -> None:
    """Require X-API-Key for remote calls (legacy /api/v1 endpoints)."""
    if _allow_local_noauth() and _is_local_request():
        return
    provided = (request.headers.get("X-API-Key") or "").strip()
    if not provided or provided != _api_key():
        abort(401, description="Unauthorized: missing/invalid X-API-Key")


def _http_request(method: str, url: str, json_body: Optional[Dict] = None) -> Tuple[int, str]:
    """
    Minimal HTTP client (stdlib) for calling our own API v2 from admin routes.
    Avoids adding requests dependency.
    """
    import json
    import urllib.request

    data = None
    headers = _api_headers().copy()
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.getcode(), body
    except Exception as e:
        return 0, str(e)


@app.route("/")
def index():
    """
    Dashboard:
    - default user is karen (query param)
    - optional top-category filters
    - optional selection mode (?mode=select&ids=1,2,3)
    - admin mode (?mode=admin) is local-only
    """
    user = request.args.get("user", "karen").strip().lower()
    mode = request.args.get("mode", "").strip().lower()
    top = request.args.get("top", "").strip()
    ids_raw = request.args.get("ids", "")

    selection_mode = mode == "select"
    admin_mode = mode == "admin"

    if admin_mode:
        _require_admin_local()

    selected_ids = _parse_ids_param(ids_raw) if selection_mode else []

    conn = get_db_connection()
    rows_base = conn.execute(
        "SELECT id, user_id, name, category, color_primary, color_variant, needs_review, context, size, notes, image_path FROM items WHERE user_id = ? ORDER BY id DESC",
        (user,),
    ).fetchall()

    # Build enriched items list
    items_all: List[Dict] = []
    top_counts: Dict[str, int] = {}

    for r in rows_base:
        d = dict(r)
        d["top_category"] = _infer_top_category(d.get("category"), d.get("name"))
        top_counts[d["top_category"]] = top_counts.get(d["top_category"], 0) + 1

        d["all_images"] = _load_images_for_item(d.get("image_path"))
        d["primary_image"] = d["all_images"][0] if d["all_images"] else None
        items_all.append(d)

    # Apply top category filter within the base set
    if top:
        items = [it for it in items_all if it.get("top_category") == top]
    else:
        items = items_all

    # Stable order of filter buttons
    top_order = [
        "Kleider",
        "Blusen & Oberteile",
        "Hosen",
        "Röcke",
        "Jacken & Mäntel",
        "Schuhe",
        "Handtaschen",
        "Accessoires",
        "Sonstiges",
    ]
    top_filters: List[Tuple[str, int]] = [(k, top_counts.get(k, 0)) for k in top_order if top_counts.get(k, 0) > 0]

    conn.close()

    ids_param = ",".join(str(i) for i in selected_ids) if selection_mode else ""

    return render_template(
        "index.html",
        user_id=user,
        items=items,
        active_top=top,
        top_filters=top_filters,
        total_count=len(items_all),
        shown_count=len(items),
        selection_mode=selection_mode,
        selected_ids=selected_ids,
        ids_param=ids_param,
        admin_mode=admin_mode,
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

    item = dict(row)
    item["top_category"] = _infer_top_category(item.get("category"), item.get("name"))
    item["all_images"] = _load_images_for_item(item.get("image_path"))
    item["primary_image"] = item["all_images"][0] if item["all_images"] else None

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

    item = dict(row)
    item["top_category"] = _infer_top_category(item.get("category"), item.get("name"))
    item["all_images"] = _load_images_for_item(item.get("image_path"))
    item["primary_image"] = item["all_images"][0] if item["all_images"] else None

    return render_template("admin_item_edit.html", user_id=user, item=item)


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

    payload = {k: v for k, v in payload.items() if not (isinstance(v, str) and v == "")}

    api_url = f"{_api_base_url()}/api/v2/items/{item_id}"
    status, body = _http_request("PATCH", api_url, json_body=payload)

    if status not in (200, 204):
        abort(500, description=f"PATCH failed: {status} {body}")

    return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")


@app.route("/admin/item/<int:item_id>/delete", methods=["POST"])
def admin_delete_item(item_id: int):
    _require_admin_local()
    user = request.args.get("user", "karen").strip().lower()

    api_url = f"{_api_base_url()}/api/v2/items/{item_id}"
    status, body = _http_request("DELETE", api_url, json_body=None)

    if status not in (200, 204):
        abort(500, description=f"DELETE failed: {status} {body}")

    return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")


# --- GPT API ENDPOINTS (Legacy, keep for compatibility; protected via X-API-Key) ---
@app.route("/api/v1/inventory", methods=["GET"])
def api_get_inventory():
    _require_api_key()
    user = request.args.get("user", "karen")

    # Be settings-aware for tests/env overrides
    try:
        settings.reload_settings()
    except Exception:
        pass

    # Backward compatible inventory: older DBs may not have newer columns yet.
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(items)").fetchall()}
        want = ["id", "name", "category", "color_primary", "color_variant", "needs_review", "context", "size", "notes", "image_path"]
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





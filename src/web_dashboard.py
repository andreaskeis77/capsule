# FILE: src/web_dashboard.py
import os
import sqlite3
import logging
import urllib.parse
from typing import Dict, List, Tuple, Optional

from flask import Flask, render_template, request, send_from_directory, jsonify, abort

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WardrobeAPI")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")
IMG_DIR = os.path.join(BASE_DIR, "02_wardrobe_images")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
flask_app = app


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(IMG_DIR, urllib.parse.unquote(filename))


def _safe_str(x: Optional[str]) -> str:
    return (x or "").strip()


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
    if any(k in blob for k in ["shoe", "footwear", "sneaker", "boot", "pump", "loafer", "sandal", "stief", "schuh"]):
        return "Schuhe"
    if any(k in blob for k in ["bag", "handbag", "purse", "tote", "clutch", "beltbag", "crossbody", "tasche", "handtasche"]):
        return "Handtaschen"
    if any(k in blob for k in ["dress", "kleid", "hemdkleid", "shirtkleid"]):
        return "Kleider"
    if any(k in blob for k in ["skirt", "rock", "roeck", "röck", "rock "]):
        return "Röcke"
    if any(k in blob for k in ["trouser", "pants", "jeans", "hose", "culotte", "leggings"]):
        return "Hosen"
    if any(k in blob for k in ["blouse", "shirt", "top", "hemd", "bluse", "tunic", "tunika"]):
        return "Blusen & Oberteile"
    if any(k in blob for k in ["jacket", "coat", "blazer", "mantel", "jacke", "cardigan", "poncho", "cape"]):
        return "Jacken & Mäntel"
    if any(k in blob for k in ["scarf", "belt", "hat", "glove", "accessor", "schmuck", "kette", "ohrr", "brosche", "gurt"]):
        return "Accessoires"

    return "Sonstiges"


def _load_images_for_item(image_path: Optional[str]) -> List[str]:
    """
    Returns URL-encoded relative file list "image_path/filename.ext" (posix) for template usage.
    """
    if not image_path:
        return []
    folder = os.path.join(IMG_DIR, image_path)
    if not os.path.exists(folder):
        return []

    imgs = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    # main.jpg first if present, then alphabetic
    imgs.sort(key=lambda x: (x.lower() != "main.jpg", x.lower()))
    return [urllib.parse.quote(f"{image_path}/{f}".replace("\\", "/")) for f in imgs]


@app.route("/")
def index():
    user = request.args.get("user", "karen").strip().lower()
    top = request.args.get("top", "").strip()

    conn = get_db_connection()

    # Load all items for this user (so we can compute counts for top categories)
    rows_all = conn.execute("SELECT * FROM items WHERE user_id = ? ORDER BY id DESC", (user,)).fetchall()

    # Build enriched items list
    items_all: List[Dict] = []
    top_counts: Dict[str, int] = {}

    for r in rows_all:
        d = dict(r)
        d["top_category"] = _infer_top_category(d.get("category"), d.get("name"))
        top_counts[d["top_category"]] = top_counts.get(d["top_category"], 0) + 1

        d["all_images"] = _load_images_for_item(d.get("image_path"))
        d["primary_image"] = d["all_images"][0] if d["all_images"] else None
        items_all.append(d)

    # Apply top category filter (Oberbegriffe)
    if top:
        items = [it for it in items_all if it.get("top_category") == top]
    else:
        items = items_all

    # Stable order of filter buttons (even if count 0, we can hide those)
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

    return render_template(
        "index.html",
        user_id=user,
        items=items,
        active_top=top,
        top_filters=top_filters,
        total_count=len(items_all),
        shown_count=len(items),
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


# --- GPT API ENDPOINTS (Legacy, keep for compatibility) ---
@app.route("/api/v1/inventory", methods=["GET"])
def api_get_inventory():
    user = request.args.get("user", "karen")
    conn = get_db_connection()
    items = [
        dict(row)
        for row in conn.execute(
            "SELECT id, name, category, color_primary FROM items WHERE user_id = ?",
            (user,),
        ).fetchall()
    ]
    conn.close()
    return jsonify({"user": user, "items": items})


@app.route("/api/v1/item/<int:item_id>", methods=["GET"])
def api_get_item_detail(item_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False)

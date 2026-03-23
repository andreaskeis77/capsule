from __future__ import annotations

import logging

from flask import Flask

from src import settings
from src.web_dashboard_routes import register_dashboard_routes
from src.web_dashboard_support import (
    admin_api_error_response,
    allow_local_noauth as _allow_local_noauth,
    api_base_url as _api_base_url,
    api_headers as _api_headers,
    api_key as _api_key,
    build_admin_patch_payload,
    ensure_db_ready as _ensure_db_ready,
    get_db_connection,
    http_request as _http_request,
    is_local_request as _is_local_request,
    load_images_for_item as _load_images_for_item,
    parse_ids_param as _parse_ids_param,
    pretty_json as _pretty_json,
    require_admin_local as _require_admin_local,
    require_api_key as _require_api_key,
    safe_str as _safe_str,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WardrobeAPI")

BASE_DIR = settings.BASE_DIR  # repo root as Path
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
flask_app = app

_handlers = register_dashboard_routes(app, logger=logger)

# Backward-compatible public names for existing imports/tests.
serve_images = _handlers.serve_images
index = _handlers.index
item_detail = _handlers.item_detail
admin_edit_item = _handlers.admin_edit_item
admin_save_item = _handlers.admin_save_item
admin_delete_item = _handlers.admin_delete_item
api_get_inventory = _handlers.api_get_inventory
api_get_item_detail = _handlers.api_get_item_detail


__all__ = [
    "BASE_DIR",
    "admin_api_error_response",
    "admin_delete_item",
    "admin_edit_item",
    "admin_save_item",
    "api_get_inventory",
    "api_get_item_detail",
    "app",
    "build_admin_patch_payload",
    "flask_app",
    "get_db_connection",
    "index",
    "item_detail",
    "logger",
    "serve_images",
    "_allow_local_noauth",
    "_api_base_url",
    "_api_headers",
    "_api_key",
    "_ensure_db_ready",
    "_http_request",
    "_is_local_request",
    "_load_images_for_item",
    "_parse_ids_param",
    "_pretty_json",
    "_require_admin_local",
    "_require_api_key",
    "_safe_str",
]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False)

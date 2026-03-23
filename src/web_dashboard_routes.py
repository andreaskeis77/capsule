from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Dict

from flask import Flask, abort, jsonify, redirect, render_template, request

from src import category_map as cm
from src import settings
from src.dashboard_category_view import build_dashboard_category_view
from src.dashboard_item_view import enrich_item_for_display, enrich_items_for_display
from src.dashboard_repository import (
    fetch_dashboard_index_rows,
    fetch_item_row_by_id,
    fetch_legacy_inventory_items,
)
from src.dashboard_request_state import parse_dashboard_request_state
from src.web_dashboard_support import (
    admin_api_error_response,
    api_base_url,
    build_admin_patch_payload,
    ensure_db_ready,
    get_db_connection,
    http_request,
    load_images_for_item,
    parse_ids_param,
    require_admin_local,
    require_api_key,
    serve_image_file,
)


@dataclass(frozen=True)
class DashboardRouteHandlers:
    serve_images: Callable[..., Any]
    index: Callable[..., Any]
    item_detail: Callable[..., Any]
    admin_edit_item: Callable[..., Any]
    admin_save_item: Callable[..., Any]
    admin_delete_item: Callable[..., Any]
    api_get_inventory: Callable[..., Any]
    api_get_item_detail: Callable[..., Any]


def register_dashboard_routes(app: Flask, *, logger) -> DashboardRouteHandlers:
    def serve_images(filename: str):
        return serve_image_file(filename)

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
            parse_ids_param=parse_ids_param,
            normalize_filter_key=cm.normalize_filter_key,
        )
        if state.admin_mode:
            require_admin_local()

        conn = get_db_connection()
        try:
            rows_base = fetch_dashboard_index_rows(conn, state.user)
        finally:
            conn.close()

        items_all = enrich_items_for_display((dict(row) for row in rows_base), load_images_for_item)
        category_view = build_dashboard_category_view(
            items_all,
            ctx=state.ctx,
            review_only=state.review_only,
            active_cat=state.active_cat,
        )
        ids_param = ",".join(str(item_id) for item_id in state.selected_ids) if state.selection_mode else ""

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

    def item_detail(item_id: int):
        """
        Detailseite für 1 Item.
        Optional ?user=karen wird nur für UI-Navigation verwendet.
        """
        user = request.args.get("user", "karen").strip().lower()
        conn = get_db_connection()
        try:
            row = fetch_item_row_by_id(conn, item_id)
        finally:
            conn.close()
        if not row:
            abort(404)

        item = enrich_item_for_display(dict(row), load_images_for_item)
        return render_template("item_detail.html", user_id=user, item=item)

    def admin_edit_item(item_id: int):
        require_admin_local()
        user = request.args.get("user", "karen").strip().lower()
        conn = get_db_connection()
        try:
            row = fetch_item_row_by_id(conn, item_id)
        finally:
            conn.close()
        if not row:
            abort(404)

        item = enrich_item_for_display(dict(row), load_images_for_item)
        return render_template(
            "admin_item_edit.html",
            user_id=user,
            item=item,
            category_admin_groups=cm.admin_option_groups(),
            category_admin_labels=cm.ADMIN_LABEL,
        )

    def admin_save_item(item_id: int):
        require_admin_local()
        user = request.args.get("user", "karen").strip().lower()
        payload = build_admin_patch_payload(request.form)
        target_url = f"{api_base_url()}/api/v2/items/{item_id}"
        status, body = http_request("PATCH", target_url, json_body=payload)
        if status not in (200, 204):
            logger.warning(
                "Admin PATCH failed: status=%s url=%s body=%s",
                status,
                target_url,
                body[:800] if body else "",
            )
            return admin_api_error_response("PATCH", status, target_url, body, user)
        return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")

    def admin_delete_item(item_id: int):
        require_admin_local()
        user = request.args.get("user", "karen").strip().lower()
        target_url = f"{api_base_url()}/api/v2/items/{item_id}"
        status, body = http_request("DELETE", target_url, json_body=None)
        if status not in (200, 204):
            logger.warning(
                "Admin DELETE failed: status=%s url=%s body=%s",
                status,
                target_url,
                body[:800] if body else "",
            )
            return admin_api_error_response("DELETE", status, target_url, body, user)
        return redirect(f"/?user={urllib.parse.quote(user)}&mode=admin")

    def api_get_inventory():
        require_api_key()
        user = request.args.get("user", "karen")
        try:
            settings.reload_settings()
        except Exception:
            pass

        conn = get_db_connection()
        try:
            items = fetch_legacy_inventory_items(conn, user)
        finally:
            conn.close()
        return jsonify({"user": user, "items": items})

    def api_get_item_detail(item_id: int):
        require_api_key()
        ensure_db_ready()
        conn = get_db_connection()
        try:
            row = fetch_item_row_by_id(conn, item_id)
        finally:
            conn.close()
        if row:
            return jsonify(dict(row))
        return jsonify({"error": "Not found"}), 404

    app.add_url_rule("/images/<path:filename>", endpoint="serve_images", view_func=serve_images)
    app.add_url_rule("/", endpoint="index", view_func=index)
    app.add_url_rule("/item/<int:item_id>", endpoint="item_detail", view_func=item_detail)
    app.add_url_rule(
        "/admin/item/<int:item_id>",
        endpoint="admin_edit_item",
        view_func=admin_edit_item,
        methods=["GET"],
    )
    app.add_url_rule(
        "/admin/item/<int:item_id>/save",
        endpoint="admin_save_item",
        view_func=admin_save_item,
        methods=["POST"],
    )
    app.add_url_rule(
        "/admin/item/<int:item_id>/delete",
        endpoint="admin_delete_item",
        view_func=admin_delete_item,
        methods=["POST"],
    )
    app.add_url_rule(
        "/api/v1/inventory",
        endpoint="api_get_inventory",
        view_func=api_get_inventory,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/item/<int:item_id>",
        endpoint="api_get_item_detail",
        view_func=api_get_item_detail,
        methods=["GET"],
    )

    return DashboardRouteHandlers(
        serve_images=serve_images,
        index=index,
        item_detail=item_detail,
        admin_edit_item=admin_edit_item,
        admin_save_item=admin_save_item,
        admin_delete_item=admin_delete_item,
        api_get_inventory=api_get_inventory,
        api_get_item_detail=api_get_item_detail,
    )


__all__ = ["DashboardRouteHandlers", "register_dashboard_routes"]

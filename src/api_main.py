# FILE: src/api_main.py
from __future__ import annotations

import importlib
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from a2wsgi import WSGIMiddleware

from src.logging_config import setup_logging, request_id_ctx

# --- Logging init ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
setup_logging(project_root=PROJECT_ROOT)

import logging  # after setup_logging
logger = logging.getLogger("wardrobe")

# --- FastAPI app ---
app = FastAPI(
    title="Wardrobe Control API",
    description="CRUD API + legacy dashboard (Flask) mounted on root.",
    version="2.0.0",
)

API_V2_IMPORT_ERROR: Optional[str] = None


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request_id_ctx.set(rid)
    request.state.request_id = rid  # important: api_v2 reads this
    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    return response


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/debug/routes", include_in_schema=False)
def debug_routes():
    routes = []
    for r in app.router.routes:
        methods = getattr(r, "methods", None)
        routes.append(
            {
                "path": getattr(r, "path", str(r)),
                "name": getattr(r, "name", None),
                "methods": sorted(list(methods)) if methods else [],
            }
        )
    return {"count": len(routes), "routes": routes, "request_id": request_id_ctx.get()}


def _mount_api_v2() -> None:
    """
    Mount FastAPI router from api_v2.
    Tries src.api_v2 first, then api_v2 for legacy layouts.
    """
    global API_V2_IMPORT_ERROR

    candidates = ("src.api_v2", "api_v2")
    last_err = None

    for mod_name in candidates:
        try:
            api_mod = importlib.import_module(mod_name)
            router = getattr(api_mod, "router", None)
            if router is None:
                raise RuntimeError(f"{mod_name} has no attribute 'router'")

            # If router already has prefix '/api/v2', don't add it again.
            router_paths = []
            for r in getattr(router, "routes", []):
                p = getattr(r, "path", "")
                if p:
                    router_paths.append(p)
            has_v2_prefix = any(p.startswith("/api/v2") for p in router_paths)

            if has_v2_prefix:
                app.include_router(router)
                logger.info("Mounted api_v2 router without extra prefix", extra={"request_id": "-"})
            else:
                app.include_router(router, prefix="/api/v2")
                logger.info("Mounted api_v2 router with prefix=/api/v2", extra={"request_id": "-"})

            # Optional init hook
            init_fn = getattr(api_mod, "init_ontology", None)
            if callable(init_fn):
                try:
                    init_fn()
                except Exception:
                    # Non-fatal
                    logger.exception("Ontology init failed; continuing without ontology.", extra={"request_id": "-"})

            API_V2_IMPORT_ERROR = None
            return

        except Exception as e:
            last_err = e
            API_V2_IMPORT_ERROR = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to import/mount {mod_name}", extra={"request_id": "-"})

    raise RuntimeError(f"api_v2 could not be imported: {API_V2_IMPORT_ERROR}") from last_err


# --- Mount v2 ---
_mount_api_v2()


# --- Mount legacy Flask dashboard on root ---
try:
    from src.web_dashboard import flask_app  # noqa

    logger.info("Using a2wsgi.WSGIMiddleware for Flask mount", extra={"request_id": "-"})
    app.mount("/", WSGIMiddleware(flask_app))
except Exception:
    logger.exception("Failed to mount Flask dashboard; API still available.", extra={"request_id": "-"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", "-")
    logger.exception("Unhandled server error", extra={"request_id": rid})
    return JSONResponse(status_code=500, content={"error": "UnhandledServerError", "request_id": rid})

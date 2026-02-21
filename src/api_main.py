# FILE: src/api_main.py
from __future__ import annotations

import importlib
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from a2wsgi import WSGIMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src import settings
from src.db_schema import ensure_schema
from src.error_contract import normalize_detail, validation_detail
from src.logging_config import request_id_ctx, setup_logging

# --- Logging init ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
setup_logging(project_root=PROJECT_ROOT)

import logging  # after setup_logging

logger = logging.getLogger("wardrobe")

API_V2_IMPORT_ERROR: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan contracts (critical path):
    - Settings are reloaded (supports tests / env overrides).
    - DB schema must be compatible with current API expectations.
    - Ontology init (non-fatal)
    """
    settings.reload_settings()
    ensure_schema()

    try:
        from src import api_v2

        api_v2.init_ontology()
    except Exception:
        logger.exception("Ontology init failed; continuing without ontology.", extra={"request_id": "-"})

    yield


app = FastAPI(
    title="Wardrobe Control API",
    description="CRUD API + legacy dashboard (Flask) mounted on root.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_and_access_log(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    token = request_id_ctx.set(rid)
    request.state.request_id = rid

    start = time.perf_counter()
    try:
        # With our exception handlers, this should return a Response even on errors.
        response = await call_next(request)
    except Exception:
        # Last-resort guard: never leak exceptions outside middleware.
        logger.exception("Exception escaped request pipeline", extra={"request_id": rid})
        detail = normalize_detail({"error": "UnhandledServerError"}, 500, rid)
        response = JSONResponse(status_code=500, content={"detail": detail})
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)

    response.headers["X-Request-Id"] = rid

    # Access log (structured via extra)
    logger.info(
        "HTTP",
        extra={
            "request_id": rid,
            "method": request.method,
            "path": request.url.path,
            "status_code": getattr(response, "status_code", None),
            "duration_ms": duration_ms,
        },
    )

    request_id_ctx.reset(token)
    return response


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/debug/routes", include_in_schema=False)
def debug_routes(request: Request):
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
    rid = getattr(request.state, "request_id", "-")
    return {"count": len(routes), "routes": routes, "request_id": rid}


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = getattr(request.state, "request_id", "-")
    detail = validation_detail(exc.errors(), rid)
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    rid = getattr(request.state, "request_id", "-")
    detail = normalize_detail(getattr(exc, "detail", None), exc.status_code, rid)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", "-")
    logger.exception("Unhandled server error", extra={"request_id": rid})
    detail = normalize_detail({"error": "UnhandledServerError"}, 500, rid)
    return JSONResponse(status_code=500, content={"detail": detail})


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

            API_V2_IMPORT_ERROR = None
            return

        except Exception as e:
            last_err = e
            API_V2_IMPORT_ERROR = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to import/mount {mod_name}", extra={"request_id": "-"})

    raise RuntimeError(f"api_v2 could not be imported: {API_V2_IMPORT_ERROR}") from last_err


# --- Mount v2 ---
_mount_api_v2()


# --- IMPORTANT: prevent Flask mount from turning missing /api/v2/* into HTML 404 ---
@app.api_route(
    "/api/v2/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def api_v2_fallback(path: str, request: Request):
    rid = getattr(request.state, "request_id", "-")
    raise HTTPException(
        status_code=404,
        detail={"error": "NotFound", "request_id": rid, "path": f"/api/v2/{path}"},
    )


# --- Mount legacy Flask dashboard on root (optional) ---
if getattr(settings, "MOUNT_FLASK", True):
    try:
        from src.web_dashboard import flask_app  # noqa

        logger.info("Using a2wsgi.WSGIMiddleware for Flask mount", extra={"request_id": "-"})
        app.mount("/", WSGIMiddleware(flask_app))
    except Exception:
        logger.exception("Failed to mount Flask dashboard; API still available.", extra={"request_id": "-"})
else:
    logger.info("Flask mount disabled (WARDROBE_MOUNT_FLASK=0)", extra={"request_id": "-"})
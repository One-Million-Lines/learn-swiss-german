"""FastAPI application factory: lifespan, middleware, error handling, routers."""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.common import tracing
from app.common.errors import ApiError
from app.config import get_settings
from app.db import client as db_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await db_client.connect(settings)
    worker_task = None
    if os.getenv("RUN_INPROCESS_WORKER", "1") == "1":
        from app.jobs.worker import run_worker
        worker_task = asyncio.create_task(run_worker("inproc"))
    try:
        yield
    finally:
        if worker_task:
            worker_task.cancel()
        await db_client.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SwissSpeak API",
        description="Dialogue-led Swiss German learning platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["ETag", "X-Request-Id"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or tracing.new_request_id()
        tracing.set_request_id(request_id)
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        body = {
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": tracing.get_request_id(),
            }
        }
        if exc.retry_after_seconds is not None:
            body["error"]["retry_after_seconds"] = exc.retry_after_seconds
        return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers)

    # Routers (imported lazily to keep import graph clean).
    from app.content.router import router as content_router, legacy_router
    from app.auth.router import router as auth_router
    from app.learning.router import router as learning_router
    from app.media.router import router as media_router
    from app.admin.router import router as admin_router

    app.include_router(content_router)
    app.include_router(legacy_router)
    app.include_router(auth_router)
    app.include_router(learning_router)
    app.include_router(media_router)
    app.include_router(admin_router)

    @app.get("/", tags=["meta"])
    async def root():
        return {"service": "swissspeak", "status": "running", "version": "1.0.0"}

    @app.get("/health/live", tags=["meta"])
    async def health_live():
        return {"status": "live"}

    @app.get("/health/ready", tags=["meta"])
    async def health_ready():
        ready = True
        checks = {}
        try:
            await db_client.get_client().admin.command("ping")
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"
            ready = False
        # Verify the migration manifest marker exists.
        try:
            db = db_client.get_db()
            migrated = await db["content_items"].estimated_document_count()
            checks["content"] = "ok" if migrated > 0 else "empty"
        except Exception:
            checks["content"] = "unavailable"
        status_code = 200 if ready else 503
        return JSONResponse(status_code=status_code, content={"status": "ready" if ready else "not_ready", "checks": checks})

    return app


app = create_app()

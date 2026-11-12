"""Ported from api/Program.cs — middleware pipeline and health endpoints.

Middleware order mirrors Program.cs: correlation-id + centralized
problem-details handler, CORS (AllowVite), rate limiter, authentication
(P0 placeholder replaced by P2), x-api-key check. Then the health endpoints
(/health/live, /health/ready, /health, /) and router registration in the
order Program.cs maps them: inline route groups first (in file order), then
the Map* endpoint modules (lines 1634-1644).

Later phases only fill in the router modules; they must never edit this file.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .db import get_engine
from .errors import ApiProblem, problem_response
from .routers import (
    admin_endpoints,
    auth_endpoints,
    chapters,
    chat_endpoints,
    courses,
    exercise_endpoints,
    import_endpoints,
    knowledge_atlas,
    lessons,
    me_endpoints,
    problems,
    reading_map,
    tasks,
    v2_endpoints,
    verticals,
)
from .routers.localization import (
    localization_endpoints,
    marketplace_endpoints,
    provider_health_endpoints,
    vendor_portal_endpoints,
)
from .schemas.base import format_dotnet_datetime
from .services.auth.current_user import ChallengeException, challenge_exception_handler
from .settings import get_api_key, get_environment, get_frontend_url

# (P2) Real authentication replaced the P0 placeholder: routers depend on
# app.services.auth.current_user directly; rate limiting lives in
# app/rate_limit.py. This module only registers the 401/403 challenge handler.


def create_app() -> FastAPI:
    environment = get_environment()
    is_production = environment.lower() == "production"
    app = FastAPI(title="StudyTracker API (Python port)")

    allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    frontend_url = get_frontend_url()
    if frontend_url.strip():
        allowed_origins.append(frontend_url.strip().rstrip("/"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_and_errors(request: Request, call_next):  # type: ignore[no-untyped-def]
        correlation_id = request.headers.get("x-correlation-id") or uuid.uuid4().hex
        request.state.correlation_id = correlation_id
        try:
            response = await call_next(request)
        except ApiProblem as exc:
            return problem_response(
                status=exc.status,
                title=exc.title,
                detail=exc.detail,
                instance=exc.instance or request.url.path,
                trace_id=correlation_id,
                type_url=exc.type_url,
            )
        except Exception as exc:  # noqa: BLE001 - centralized handler mirrors Program.cs
            detail = str(exc) if environment.lower() == "development" else (
                "Internal server error. Please refer to traceId for support."
            )
            return problem_response(
                status=500,
                title="An internal error occurred processing your request.",
                detail=detail,
                instance=request.url.path,
                trace_id=correlation_id,
                type_url="https://tools.ietf.org/html/rfc7231#section-6.6.1",
            )
        response.headers["x-correlation-id"] = correlation_id
        return response

    @app.middleware("http")
    async def api_key_check(request: Request, call_next):  # type: ignore[no-untyped-def]
        path = request.url.path
        if path.startswith("/health") or path.startswith("/swagger") or request.method == "OPTIONS":
            return await call_next(request)
        expected = get_api_key()
        if not expected.strip():
            if is_production:
                return problem_response(
                    status=500,
                    title="Internal Server Error",
                    detail="API key configuration is required in production.",
                    instance=path,
                    trace_id=getattr(request.state, "correlation_id", ""),
                    type_url="https://tools.ietf.org/html/rfc7231#section-6.6.1",
                )
            return await call_next(request)
        if request.headers.get("x-api-key") != expected:
            return problem_response(
                status=401,
                title="Unauthorized",
                detail="Invalid or missing API Key.",
                instance=path,
                trace_id=getattr(request.state, "correlation_id", ""),
                type_url="https://tools.ietf.org/html/rfc7235#section-3.1",
            )
        return await call_next(request)

    @app.exception_handler(ApiProblem)
    async def api_problem_handler(request: Request, exc: ApiProblem) -> JSONResponse:
        return problem_response(
            status=exc.status,
            title=exc.title,
            detail=exc.detail,
            instance=exc.instance or request.url.path,
            trace_id=getattr(request.state, "correlation_id", ""),
            type_url=exc.type_url,
        )

    app.add_exception_handler(ChallengeException, challenge_exception_handler)

    @app.get("/health/live", name="HealthLiveCheck")
    async def health_live() -> dict[str, object]:
        return {"status": "Live", "timestamp": _utcnow_iso()}

    @app.get("/health/ready", name="HealthReadyCheck")
    async def health_ready() -> Response:
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                applied = await conn.execute(text("SELECT COUNT(*) FROM \"__EFMigrationsHistory\""))
                count = applied.scalar() or 0
            return JSONResponse(
                {
                    "status": "Ready",
                    "database": "Connected",
                    "appliedMigrationsCount": count,
                    "timestamp": _utcnow_iso(),
                }
            )
        except Exception:  # noqa: BLE001 - readiness reports unhealthy, mirrors C#
            return JSONResponse(
                status_code=503,
                content={
                    "status": "Unhealthy",
                    "error": "Database readiness check encountered an error",
                    "timestamp": _utcnow_iso(),
                },
            )

    @app.get("/health", name="HealthCheck")
    async def health() -> Response:
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return JSONResponse(
                {"status": "Healthy", "database": "Connected", "timestamp": _utcnow_iso()}
            )
        except Exception:  # noqa: BLE001 - mirrors C# fallback
            return JSONResponse(
                status_code=503,
                content={"status": "Unhealthy", "error": "Database connection error"},
            )

    @app.get("/")
    async def root() -> str:
        return "StudyTracker API is running. Use /health for service health."

    # Router registration order mirrors Program.cs: inline groups in file order,
    # then Map* modules in lines 1634-1644 order.
    app.include_router(verticals.router)
    app.include_router(tasks.router)
    app.include_router(courses.router)
    app.include_router(lessons.router)
    app.include_router(problems.router)
    app.include_router(knowledge_atlas.router)
    app.include_router(reading_map.router)
    app.include_router(chapters.router)
    app.include_router(v2_endpoints.router)
    app.include_router(import_endpoints.router)
    app.include_router(exercise_endpoints.router)
    app.include_router(localization_endpoints.router)
    app.include_router(marketplace_endpoints.router)
    app.include_router(vendor_portal_endpoints.router)
    app.include_router(provider_health_endpoints.router)
    app.include_router(auth_endpoints.router)
    app.include_router(me_endpoints.router)
    app.include_router(admin_endpoints.router)
    app.include_router(chat_endpoints.router)

    return app


def _utcnow_iso() -> str:
    return format_dotnet_datetime(datetime.now(UTC))


app = create_app()

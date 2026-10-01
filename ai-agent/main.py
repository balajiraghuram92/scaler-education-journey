"""FastAPI app factory.

Run with ``uvicorn main:create_app --factory``. Importing this module has no
side effects; configuration is validated when the app is created, and a bad
environment exits with a one-line error instead of a traceback.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

import config
import db
import observability
from rate_limit import SlidingWindowLimiter
from routers import echo, graph_demo, health, identity

logger = logging.getLogger("ai_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    observability.init_observability(app.state.settings.langfuse_enabled)
    # open(wait=False): start even if the DB is not reachable yet;
    # /health stays a pure liveness probe, /health/ready reports the DB.
    await app.state.pool.open(wait=False)
    try:
        yield
    finally:
        await app.state.pool.close()
        observability.shutdown_observability()


def build_app(settings: config.Settings) -> FastAPI:
    docs = settings.enable_docs
    app = FastAPI(
        title="Neuralascent ai-agent",
        lifespan=lifespan,
        docs_url="/docs" if docs else None,
        redoc_url="/redoc" if docs else None,
        openapi_url="/openapi.json" if docs else None,
    )
    app.state.settings = settings
    app.state.pool = db.create_pool(settings.database_conninfo)
    app.state.rate_limiter = SlidingWindowLimiter(settings.rate_limit_per_minute)

    app.include_router(health.router)
    app.include_router(identity.router)
    app.include_router(echo.router)
    app.include_router(graph_demo.router)
    return app


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        settings = config.get_settings()
    except config.ConfigError as exc:
        print(f"ai-agent startup error: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from None
    return build_app(settings)

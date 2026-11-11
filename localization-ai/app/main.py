"""FastAPI app factory.

Run with ``uvicorn app.main:create_app --factory`` from ``localization-ai/``.
Importing this module has no side effects; configuration is validated when
the app is created, and a bad environment exits with a one-line error
instead of a traceback.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError
from psycopg_pool import AsyncConnectionPool

from app import db as db_module
from app.evals.comet import CometKiwiScorer
from app.providers import build_chat_provider, build_embedding_provider
from app.providers.base import ChatProvider, EmbeddingProvider
from app.routers import eval as eval_router
from app.routers import health as health_router
from app.routers import pipeline as pipeline_router
from app.settings import Settings

logger = logging.getLogger("localization_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if app.state.settings.comet_enabled:
        scorer = CometKiwiScorer(app.state.settings.comet_model, gpus=app.state.settings.comet_gpus)
        if scorer.load():
            app.state.comet_scorer = scorer
        else:
            logger.warning("COMET-Kiwi unavailable (%s); runs will record null for the metric", scorer.status)
    # open(wait=False): start even if the DB is not reachable yet;
    # /health stays a pure liveness probe, /health/ready reports the DB.
    await app.state.pool.open(wait=False)
    try:
        yield
    finally:
        await app.state.chat_provider.close()
        await app.state.embedding_provider.close()
        await app.state.pool.close()


def build_app(
    settings: Settings,
    *,
    pool: AsyncConnectionPool | None = None,
    chat_provider: ChatProvider | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> FastAPI:
    docs = settings.enable_docs
    app = FastAPI(
        title="Neuralascent localization-ai",
        lifespan=lifespan,
        docs_url="/docs" if docs else None,
        redoc_url="/redoc" if docs else None,
        openapi_url="/openapi.json" if docs else None,
    )
    app.state.settings = settings
    app.state.pool = pool or db_module.create_pool(settings.database_conninfo())
    app.state.chat_provider = chat_provider or build_chat_provider(settings)
    app.state.embedding_provider = embedding_provider or build_embedding_provider(settings)
    app.state.comet_scorer = None

    app.include_router(health_router.router)
    app.include_router(eval_router.router)
    app.include_router(pipeline_router.router)
    return app


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        settings = Settings()
    except ValidationError as exc:
        print(f"localization-ai startup error: {exc.errors()[0]['msg']}", file=sys.stderr, flush=True)
        raise SystemExit(1) from None
    if not settings.api_shared_secret:
        print("localization-ai startup error: API_SHARED_SECRET is unset", file=sys.stderr, flush=True)
        raise SystemExit(1) from None
    return build_app(settings)

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health():
    """Liveness: the process is up. Never touches the database."""
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(request: Request):
    """Readiness: database reachable and pgvector extension present."""
    try:
        async with request.app.state.pool.connection(timeout=3) as conn:
            cur = await conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            has_vector = await cur.fetchone() is not None
    except Exception:
        logger.warning("readiness check: database unreachable", exc_info=True)
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "down"})
    return {"status": "ready", "database": "ok", "vector_extension": has_vector}

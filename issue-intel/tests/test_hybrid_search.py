"""Full-text search matches any query term (needs DB)."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import delete, func

from app.governance.rls import service_session
from app.ingest.normalise import get_or_create_acl
from app.models.g1 import Chunk
from app.search.hybrid import hybrid_search
from tests.db_helper import ensure_test_db

NEAR_TEXT = "tessera editor crashes on startup with null workspace"
FAR_TEXT = "unrelated content about weather forecasts and rainfall"
QUERY = "tessera editor crash startup workspace plugin"


async def _seed() -> tuple[str, str]:
    near_key = f"FT-NEAR-{uuid.uuid4().hex[:8]}"
    far_key = f"FT-FAR-{uuid.uuid4().hex[:8]}"
    async with service_session() as session:
        acl = await get_or_create_acl(session, "UiState", "Support", "OPEN")
        await session.flush()
        session.add(
            Chunk(
                owner_type="case", owner_key=near_key, seq=0, text=NEAR_TEXT,
                embedding=[0.0] * 64,
                tsv=func.to_tsvector("english", NEAR_TEXT), acl_id=acl.id,
            )
        )
        session.add(
            Chunk(
                owner_type="case", owner_key=far_key, seq=0, text=FAR_TEXT,
                embedding=[0.0] * 64,
                tsv=func.to_tsvector("english", FAR_TEXT), acl_id=acl.id,
            )
        )
        await session.commit()
    return near_key, far_key


async def _cleanup(near_key: str, far_key: str) -> None:
    async with service_session() as session:
        await session.execute(
            delete(Chunk).where(Chunk.owner_key.in_([near_key, far_key]))
        )
        await session.commit()


def test_fulltext_matches_any_term(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)

    async def _search() -> list[str]:
        async with service_session() as session:
            hits = await hybrid_search(session, QUERY, [0.0] * 64, mode="fulltext")
            return [h.owner_key for h in hits]

    near_key, far_key = asyncio.run(_seed())
    try:
        keys = asyncio.run(_search())
        assert near_key in keys
        assert far_key not in keys
    finally:
        asyncio.run(_cleanup(near_key, far_key))

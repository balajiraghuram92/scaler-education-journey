"""Ingestion idempotency against postgres. Skips without a test database."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.db import create_session_factory
from app.gateway.adapters import FakeAdapter
from app.gateway.gateway import ModelGateway
from app.ingest.run import run_ingest
from app.models.g1 import Case, Chunk, Link
from app.settings import Settings
from synthetic.generate import run_generator
from tests.db_helper import ensure_test_db


def _counts(url: str) -> tuple[int, int, int]:
    async def _run() -> tuple[int, int, int]:
        factory = create_session_factory(Settings(database_url=url))
        async with factory() as session:
            n_cases = (await session.execute(select(func.count(Case.id)))).scalar() or 0
            n_chunks = (await session.execute(select(func.count(Chunk.id)))).scalar() or 0
            n_links = (await session.execute(select(func.count(Link.id)))).scalar() or 0
        return n_cases, n_chunks, n_links

    return asyncio.run(_run())


def test_ingest_twice_changes_nothing(tmp_path: Path) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    run_generator(seed=20240917, out_dir=tmp_path)
    scripted = FakeAdapter(default='{"outcome": "FIXED"}')

    async def _ingest() -> dict[str, int]:
        factory = create_session_factory(Settings(database_url=url))
        gateway = ModelGateway(settings=Settings(database_url=url), adapter=scripted)
        async with factory() as session:
            return await run_ingest(session, gateway, tmp_path / "corpus")

    asyncio.run(_ingest())
    before = _counts(url)
    second = asyncio.run(_ingest())
    after = _counts(url)
    assert before == after
    assert second["links"] == 0
    assert second["outcomes"] == 0
    assert second["chunks"] == 0

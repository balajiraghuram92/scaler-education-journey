"""Shared pytest fixtures.

Write tests use the scratch database `studytracker_py` (see README for setup)
and roll back after every test. The main local database is never written by tests.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _scratch_url() -> str:
    return os.environ.get(
        "PY_SCRATCH_DATABASE_URL",
        "postgresql+asyncpg://studyuser:studyuserpass@localhost:5432/studytracker_py",
    )


_postgres_probe_cache: dict[str, bool] = {}


async def _try_connect(url: str) -> bool:
    try:
        engine = create_async_engine(url)
        try:
            async with engine.connect():
                pass
        finally:
            await engine.dispose()
        return True
    except Exception:
        return False


async def require_postgres(url: str | None = None) -> str:
    """Skip the calling test unless PostgreSQL answers.

    Probes once per URL per session; mirrors the Docker-backed skip pattern
    (plain pytest.skip with a reason) used by the exercise runner tests.
    """
    target = url or _scratch_url()
    if target not in _postgres_probe_cache:
        _postgres_probe_cache[target] = await _try_connect(target)
    if not _postgres_probe_cache[target]:
        pytest.skip(f"no PostgreSQL at {target}")
    return target


@pytest_asyncio.fixture
async def scratch_session() -> AsyncIterator[AsyncSession]:
    await require_postgres()
    engine = create_async_engine(_scratch_url(), pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()

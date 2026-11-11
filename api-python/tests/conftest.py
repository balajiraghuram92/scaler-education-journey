"""Shared pytest fixtures.

Write tests use the scratch database `studytracker_py` (see README for setup)
and roll back after every test. The main local database is never written by tests.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _scratch_url() -> str:
    return os.environ.get(
        "PY_SCRATCH_DATABASE_URL",
        "postgresql+asyncpg://studyuser:studyuserpass@localhost:5432/studytracker_py",
    )


@pytest_asyncio.fixture
async def scratch_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(_scratch_url(), pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()

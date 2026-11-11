"""RLS tests: unentitled users get zero rows on every query path."""
from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select, text

from app.db import create_session_factory
from app.governance.entitlements import Entitlements
from app.governance.rls import rls_session
from app.ingest.normalise import get_or_create_acl
from app.models.g1 import Case, Change, Chunk, Thread
from app.settings import Settings
from tests.db_helper import ensure_test_db


def _seed(url: str) -> None:
    async def _run() -> None:
        factory = create_session_factory(Settings(database_url=url))
        async with factory() as session:
            async with session.begin():
                await session.execute(text("SET LOCAL app.modules = :v"), {"v": "UiState"})
                await session.execute(text("SET LOCAL app.departments = :v"), {"v": "SE"})
                await session.execute(text("SET LOCAL app.max_restriction = :v"), {"v": "2"})
                open_acl = await get_or_create_acl(session, "UiState", "Support", "OPEN")
                se_acl = await get_or_create_acl(session, "VersionControl", "SE", "SE")
                session.add(
                    Case(source="TEST", source_key="RLS-OPEN", module="UiState",
                         filed_module="UiState", title="open", body="b", version="v",
                         status="Open", acl_id=open_acl.id)
                )
                session.add(
                    Case(source="TEST", source_key="RLS-SE", module="VersionControl",
                         filed_module="VersionControl", title="se", body="b", version="v",
                         status="Open", acl_id=se_acl.id)
                )

    asyncio.run(_run())


def _cleanup(url: str) -> None:
    async def _run() -> None:
        factory = create_session_factory(Settings(database_url=url))
        async with factory() as session:
            async with session.begin():
                await session.execute(
                    text("DELETE FROM cases WHERE source = 'TEST'")
                )

    asyncio.run(_run())


def test_unentitled_user_sees_zero_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)
    _seed(url)
    try:

        async def _query(ent: Entitlements) -> tuple[int, int, int, int, int]:
            async with rls_session(ent) as session:
                n_orm = len((await session.execute(select(Case))).scalars().all())
                n_raw = len(
                    (await session.execute(text("SELECT id FROM cases"))).all()
                )
                n_threads = len((await session.execute(select(Thread))).scalars().all())
                n_changes = len((await session.execute(select(Change))).scalars().all())
                n_chunks = len((await session.execute(select(Chunk))).scalars().all())
            return n_orm, n_raw, n_threads, n_changes, n_chunks

        none_ent = Entitlements()
        assert asyncio.run(_query(none_ent)) == (0, 0, 0, 0, 0)
        open_ent = Entitlements({"UiState"}, {"Support"}, 0)
        n_orm, n_raw, _, _, _ = asyncio.run(_query(open_ent))
        assert n_orm == n_raw == 1
    finally:
        _cleanup(url)

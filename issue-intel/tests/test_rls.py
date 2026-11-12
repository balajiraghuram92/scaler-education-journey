"""RLS tests: unentitled users get zero rows on every query path."""
from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.governance.entitlements import Entitlements
from app.governance.rls import rls_session, service_session
from app.ingest.normalise import get_or_create_acl
from app.models.g1 import Case, Change, Chunk, Thread
from tests.db_helper import ensure_test_db


def _seed(url: str) -> None:
    async def _run() -> None:
        async with service_session() as session:
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
            await session.commit()

    asyncio.run(_run())


def _cleanup(url: str) -> None:
    async def _run() -> None:
        async with service_session() as session:
            await session.execute(
                text("DELETE FROM cases WHERE source = 'TEST'")
            )
            await session.commit()

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
                n_orm = len(
                    (
                        await session.execute(
                            select(Case).where(Case.source == "TEST")
                        )
                    )
                    .scalars()
                    .all()
                )
                n_raw = len(
                    (
                        await session.execute(
                            text("SELECT id FROM cases WHERE source = 'TEST'")
                        )
                    ).all()
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
        full_orm, full_raw, _, _, _ = asyncio.run(_query(Entitlements.service()))
        assert full_orm == full_raw == 2

        async def _whoami() -> str:
            async with rls_session(open_ent) as session:
                row = await session.execute(text("SELECT current_user"))
                return str(row.scalar_one())

        assert asyncio.run(_whoami()) == "issueintel_app"
    finally:
        _cleanup(url)


def test_insert_outside_entitlement_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)

    async def _acl_id() -> int:
        async with service_session() as session:
            se_acl = await get_or_create_acl(session, "VersionControl", "SE", "SE")
            await session.commit()
            return int(se_acl.id)

    acl_id = asyncio.run(_acl_id())

    async def _attempt() -> None:
        async with rls_session(
            Entitlements({"UiState"}, {"Support"}, 0)
        ) as session:
            session.add(
                Case(source="TEST", source_key="RLS-REFUSED",
                     module="VersionControl", filed_module="VersionControl",
                     title="x", body="b", version="v", status="Open",
                     acl_id=acl_id)
            )
            await session.flush()

    with pytest.raises(DBAPIError):
        asyncio.run(_attempt())

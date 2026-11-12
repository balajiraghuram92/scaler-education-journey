"""service_session exit behaviour (needs DB): detached rows stay readable,
and a failed flush still surfaces the original error, not PendingRollbackError."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.governance.rls import service_session
from app.models.g2 import Run
from tests.db_helper import ensure_test_db


def _run_id() -> str:
    return f"sess-{uuid.uuid4().hex[:12]}"


async def _insert_run(run_id: str) -> None:
    async with service_session() as session:
        session.add(
            Run(
                id=run_id,
                ticket_source="TEST",
                ticket_key="TOK",
                trigger="test",
                pipeline_version="v0",
                content_hash="0" * 64,
            )
        )
        await session.commit()


async def _delete_run(run_id: str) -> None:
    async with service_session() as session:
        await session.execute(delete(Run).where(Run.id == run_id))
        await session.commit()


def test_row_loaded_inside_block_is_readable_after_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)
    run_id = _run_id()

    async def _load() -> Run:
        async with service_session() as session:
            return (
                await session.execute(select(Run).where(Run.id == run_id))
            ).scalar_one()

    asyncio.run(_insert_run(run_id))
    try:
        row = asyncio.run(_load())
        assert row.ticket_key == "TOK"
    finally:
        asyncio.run(_delete_run(run_id))


def test_failed_flush_surfaces_original_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)
    run_id = _run_id()

    async def _duplicate() -> None:
        async with service_session() as session:
            session.add(
                Run(
                    id=run_id,
                    ticket_source="TEST",
                    ticket_key="TOK",
                    trigger="test",
                    pipeline_version="v0",
                    content_hash="0" * 64,
                )
            )
            await session.flush()
            session.add(
                Run(
                    id=run_id,
                    ticket_source="TEST",
                    ticket_key="TOK",
                    trigger="test",
                    pipeline_version="v0",
                    content_hash="0" * 64,
                )
            )
            await session.flush()

    asyncio.run(_insert_run(run_id))
    try:
        with pytest.raises(IntegrityError):
            asyncio.run(_duplicate())
    finally:
        asyncio.run(_delete_run(run_id))

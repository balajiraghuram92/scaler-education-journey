"""Approval token tests: expired, reused, wrong-payload, forged (needs DB)."""
from __future__ import annotations

import asyncio
import hashlib
import uuid

import pytest
from sqlalchemy import delete

from app.governance.rls import service_session
from app.governance.tokens import mint_token, validate_token
from app.models.g2 import Run
from app.models.g3 import ApprovalToken
from tests.db_helper import ensure_test_db


def _make_runs(run_ids: list[str]) -> None:
    async def _run() -> None:
        async with service_session() as session:
            for run_id in run_ids:
                session.add(
                    Run(
                        id=run_id,
                        ticket_source="TEST",
                        ticket_key="TOK",
                        trigger="test",
                        pipeline_version="v0",
                        content_hash=hashlib.sha256(run_id.encode()).hexdigest(),
                    )
                )
            await session.commit()

    asyncio.run(_run())


def _delete_runs_and_tokens(run_ids: list[str]) -> None:
    async def _run() -> None:
        async with service_session() as session:
            await session.execute(
                delete(ApprovalToken).where(ApprovalToken.run_id.in_(run_ids))
            )
            await session.execute(delete(Run).where(Run.id.in_(run_ids)))
            await session.commit()

    asyncio.run(_run())


def test_token_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)
    run1 = f"tok-{uuid.uuid4().hex[:12]}"
    _make_runs([run1])

    async def _run() -> None:
        token = await mint_token(run1, "TES-1", "merge_pr", {"pr_id": 1})
        assert await validate_token(token, "merge_pr", run1, "TES-1", {"pr_id": 999}) is False
        assert await validate_token(token, "merge_pr", run1, "TES-1", {"pr_id": 1})
        assert not await validate_token(token, "merge_pr", run1, "TES-1", {"pr_id": 1})

    try:
        asyncio.run(_run())
    finally:
        _delete_runs_and_tokens([run1])


def test_token_rejections(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)
    run2 = f"tok-{uuid.uuid4().hex[:12]}"
    run3 = f"tok-{uuid.uuid4().hex[:12]}"
    _make_runs([run2, run3])

    async def _run() -> None:
        assert not await validate_token("forged-token", "merge_pr", "r", "T", {})
        token = await mint_token(run2, "TES-2", "merge_pr", {"pr_id": 2})
        assert not await validate_token(token, "merge_pr", run2, "TES-2", {"pr_id": 3})
        assert not await validate_token(token, "publish_status", run2, "TES-2",
                                        {"pr_id": 2})
        assert not await validate_token(token, "merge_pr", "other", "TES-2",
                                        {"pr_id": 2})
        expired = await mint_token(run3, "TES-3", "merge_pr", {}, ttl_seconds=-1)
        assert not await validate_token(expired, "merge_pr", run3, "TES-3", {})

    try:
        asyncio.run(_run())
    finally:
        _delete_runs_and_tokens([run2, run3])

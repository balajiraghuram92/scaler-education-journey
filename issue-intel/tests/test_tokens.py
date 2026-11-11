"""Approval token tests: expired, reused, wrong-payload, forged (needs DB)."""
from __future__ import annotations

import asyncio

import pytest

from app.governance.tokens import mint_token, validate_token
from tests.db_helper import ensure_test_db


def test_token_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)

    async def _run() -> None:
        token = await mint_token("run1", "TES-1", "merge_pr", {"pr_id": 1})
        assert await validate_token(token, "merge_pr", "run1", "TES-1", {"pr_id": 999}) is False
        assert await validate_token(token, "merge_pr", "run1", "TES-1", {"pr_id": 1})
        assert not await validate_token(token, "merge_pr", "run1", "TES-1", {"pr_id": 1})

    asyncio.run(_run())


def test_token_rejections(monkeypatch: pytest.MonkeyPatch) -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")
    monkeypatch.setenv("ISSUEINTEL_DATABASE_URL", url)

    async def _run() -> None:
        assert not await validate_token("forged-token", "merge_pr", "r", "T", {})
        token = await mint_token("run2", "TES-2", "merge_pr", {"pr_id": 2})
        assert not await validate_token(token, "merge_pr", "run2", "TES-2", {"pr_id": 3})
        assert not await validate_token(token, "publish_status", "run2", "TES-2",
                                        {"pr_id": 2})
        assert not await validate_token(token, "merge_pr", "other", "TES-2",
                                        {"pr_id": 2})
        expired = await mint_token("run3", "TES-3", "merge_pr", {}, ttl_seconds=-1)
        assert not await validate_token(expired, "merge_pr", "run3", "TES-3", {})

    asyncio.run(_run())

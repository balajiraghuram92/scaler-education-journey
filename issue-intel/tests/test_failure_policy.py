"""Failure-policy tests: one for each class of error (no DB)."""
from __future__ import annotations

import asyncio

import pytest

from app.pipeline.stages import (
    CitationError,
    FatalError,
    LeakageError,
    MalformedJsonError,
    ModelTimeoutError,
    RateLimitError,
    SchemaValidationError,
    TransientError,
    execute_with_retry,
)


def test_transient_retries_then_succeeds() -> None:
    calls = 0

    async def flaky() -> dict:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RateLimitError("slow down")
        return {"ok": True}

    result, attempts = asyncio.run(execute_with_retry(flaky))
    assert result == {"ok": True}
    assert attempts == 3
    assert calls == 3


def test_transient_gives_up_after_three_attempts() -> None:
    calls = 0

    async def always_timeout() -> dict:
        nonlocal calls
        calls += 1
        raise ModelTimeoutError("timed out")

    with pytest.raises(ModelTimeoutError):
        asyncio.run(execute_with_retry(always_timeout))
    assert calls == 3


def test_malformed_json_is_transient() -> None:
    calls = 0

    async def bad_then_good() -> dict:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise MalformedJsonError("not json")
        return {"ok": True}

    result, attempts = asyncio.run(execute_with_retry(bad_then_good))
    assert result == {"ok": True}
    assert attempts == 2


def test_fatal_errors_raise_immediately() -> None:
    for error in (
        SchemaValidationError("schema"),
        CitationError("cite"),
        LeakageError("leak"),
    ):
        calls = 0

        async def fatal() -> dict:
            nonlocal calls
            calls += 1
            raise error

        with pytest.raises(type(error)):
            asyncio.run(execute_with_retry(fatal))
        assert calls == 1


def test_unexpected_errors_raise_immediately() -> None:
    calls = 0

    async def broken() -> dict:
        nonlocal calls
        calls += 1
        raise ValueError("boom")

    with pytest.raises(ValueError):
        asyncio.run(execute_with_retry(broken))
    assert calls == 1


def test_error_hierarchy() -> None:
    for transient in (RateLimitError, ModelTimeoutError, MalformedJsonError):
        assert issubclass(transient, TransientError)
    for fatal in (SchemaValidationError, CitationError, LeakageError):
        assert issubclass(fatal, FatalError)
        assert not issubclass(fatal, TransientError)

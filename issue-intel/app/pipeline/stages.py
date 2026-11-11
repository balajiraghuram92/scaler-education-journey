"""Stages S1..S8: failure policy, retry wrapper and shared context.

Failure policy: only transient errors (rate limit, timeout, malformed JSON)
retry, at most twice. Any other failure stops the run at FAILED_AWAITING_HUMAN.
No stage is ever skipped silently.
"""
from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gateway.gateway import ModelGateway
from app.models.g1 import Case
from app.models.g2 import Evidence, Run, RunStage


class StageError(Exception):
    """Base class for stage failures."""


class TransientError(StageError):
    """May succeed on retry."""


class RateLimitError(TransientError):
    pass


class ModelTimeoutError(TransientError):
    pass


class MalformedJsonError(TransientError):
    pass


class FatalError(StageError):
    """Never retried."""


class SchemaValidationError(FatalError):
    pass


class CitationError(FatalError):
    pass


class LeakageError(FatalError):
    pass


MAX_ATTEMPTS = 3

S1_SYSTEM = (
    "Parse the ticket. Reply with JSON only: "
    '{"module": "...", "version": "...", "error_strings": [...], '
    '"stack_frames": [...], "legacy_ids": [...]}.'
)
S2_SYSTEM = (
    "Decide whether the ticket is filed under the right module. Reply with "
    'JSON only: {"predicted_module": "...", "confidence": 0.0-1.0}.'
)
S5_SYSTEM = (
    "Judge whether the change could have caused the issue. Reply with JSON "
    'only: {"relevant": true|false, "score": 0.0-1.0}.'
)
S7_SYSTEM = (
    "Write the investigation answer from the evidence only: seen before?, "
    "outcomes, likely cause, fix or workaround, who to ask now. Every claim "
    "must cite evidence ids. Reply with JSON only: "
    '{"seen_before": true|false, "outcomes": [...], "likely_cause": "...", '
    '"fix_or_workaround": "...", "who_to_ask": "...", "confidence": 0.0-1.0, '
    '"claims": [{"text": "...", "cites": ["E1"]}]}.'
)
CUST_RE = re.compile(r"CUST-\d+")


@dataclass
class RunContext:
    session: AsyncSession
    gateway: ModelGateway
    run: Run
    ticket: Case
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)


async def add_evidence(
    ctx: RunContext, kind: str, key: str, title: str, snippet: str,
    outcome: str, acl_id: int, data: dict[str, Any] | None = None,
) -> str:
    evid = f"E{len(ctx.evidence) + 1}"
    row = Evidence(
        run_id=ctx.run.id, evid=evid, kind=kind, key=key, title=title,
        snippet=snippet[:2000], outcome=outcome, acl_id=acl_id, data=data or {},
    )
    ctx.session.add(row)
    ctx.evidence.append(row)
    await ctx.session.flush()
    return evid


def parse_json_or_raise(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise MalformedJsonError(f"model returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise MalformedJsonError("model JSON is not an object")
    return payload


async def execute_with_retry(
    fn: Callable[[], Awaitable[dict[str, Any]]],
) -> tuple[dict[str, Any], int]:
    """Attempt loop without DB access: transient retries twice, fatal raises."""
    last: TransientError | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return await fn(), attempt
        except TransientError as exc:
            last = exc
    assert last is not None
    raise last


async def run_stage(
    ctx: RunContext,
    stage: str,
    input_payload: dict[str, Any],
    fn: Callable[[], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    """Run one stage with the failure policy; exactly one row per stage."""
    row = (
        await ctx.session.execute(
            select(RunStage).where(RunStage.run_id == ctx.run.id, RunStage.stage == stage)
        )
    ).scalar_one_or_none()
    if row is None:
        row = RunStage(run_id=ctx.run.id, stage=stage, status="RUNNING")
        ctx.session.add(row)
    row.input_json = input_payload
    row.status = "RUNNING"
    await ctx.session.flush()
    before = len(ctx.gateway.logged_calls)
    attempt = 1
    try:
        while True:
            try:
                output = await fn()
                break
            except TransientError as exc:
                row.attempt = attempt
                row.error = f"{type(exc).__name__}: {exc}"
                await ctx.session.flush()
                attempt += 1
                if attempt > MAX_ATTEMPTS:
                    raise
    except TransientError as exc:
        row.status = "FAILED"
        row.error = f"{type(exc).__name__}: {exc} (after {MAX_ATTEMPTS} attempts)"
        await ctx.session.commit()
        raise
    except (FatalError, Exception) as exc:
        row.status = "FAILED"
        row.error = f"{type(exc).__name__}: {exc}"
        await ctx.session.commit()
        raise
    delta = ctx.gateway.logged_calls[before:]
    row.output_json = output
    row.status = "DONE"
    row.attempt = attempt
    row.model = delta[-1].model if delta else ""
    row.tokens_in = sum(c.tokens_in for c in delta)
    row.tokens_out = sum(c.tokens_out for c in delta)
    row.latency_ms = sum(c.latency_ms for c in delta)
    await ctx.session.commit()
    return output

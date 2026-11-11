"""Approval tokens: short-lived, single-use, bound to run + ticket + payload."""
from __future__ import annotations

import datetime
import hashlib
import json
import secrets
from typing import Any

from sqlalchemy import select

from app.governance.rls import service_session
from app.models.g3 import ApprovalToken
from app.settings import get_settings


def payload_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def _token_hash(token: str) -> str:
    secret = get_settings().approval_secret
    return hashlib.sha256(f"{secret}:{token}".encode()).hexdigest()


async def mint_token(
    run_id: str, ticket_key: str, action: str, payload: dict[str, Any],
    ttl_seconds: int | None = None,
) -> str:
    token = secrets.token_urlsafe(32)
    ttl = ttl_seconds if ttl_seconds is not None else get_settings().approval_token_ttl_seconds
    async with service_session() as session:
        session.add(
            ApprovalToken(
                token_hash=_token_hash(token), run_id=run_id, ticket_key=ticket_key,
                payload_hash=payload_hash(payload), action=action, used=False,
                expires_at=datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(seconds=ttl),
            )
        )
        await session.commit()
    return token


async def validate_token(
    token: str, action: str, run_id: str, ticket_key: str,
    payload: dict[str, Any],
) -> bool:
    """Single-use validation: success marks the token used."""
    async with service_session() as session:
        row = (
            await session.execute(
                select(ApprovalToken).where(ApprovalToken.token_hash == _token_hash(token))
            )
        ).scalar_one_or_none()
        if row is None:
            return False
        if row.used:
            return False
        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=datetime.UTC)
        if expires <= datetime.datetime.now(datetime.UTC):
            return False
        if row.action != action or row.run_id != run_id or row.ticket_key != ticket_key:
            return False
        if row.payload_hash != payload_hash(payload):
            return False
        row.used = True
        await session.commit()
        return True

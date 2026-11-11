"""Versioned model routing: exactly one active version; audited switching."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g4 import RoutingVersion


@dataclass
class Route:
    primary: str
    fallback: str
    token_limit: int
    mode: str  # SYNC | BATCH
    canary_module: str | None = None
    canary_model: str | None = None
    canary_share: float = 0.0


def route_from_dict(task: str, payload: dict[str, Any]) -> Route:
    entry = payload.get(task, {})
    return Route(
        primary=str(entry.get("primary", "tessera-small")),
        fallback=str(entry.get("fallback", "tessera-large")),
        token_limit=int(entry.get("token_limit", 8000)),
        mode=str(entry.get("mode", "SYNC")),
        canary_module=entry.get("canary_module"),
        canary_model=entry.get("canary_model"),
        canary_share=float(entry.get("canary_share", 0.0)),
    )


async def get_active(session: AsyncSession) -> RoutingVersion | None:
    return (
        await session.execute(
            select(RoutingVersion).where(RoutingVersion.active.is_(True))
        )
    ).scalar_one_or_none()


async def create_version(
    session: AsyncSession, routes: dict[str, Any], note: str
) -> int:
    latest = (
        await session.execute(
            select(RoutingVersion).order_by(RoutingVersion.version.desc()).limit(1)
        )
    ).scalar_one_or_none()
    number = (latest.version + 1) if latest else 1
    session.add(RoutingVersion(version=number, routes=routes, active=False,
                               note=note))
    await session.commit()
    return number


async def switch_version(session: AsyncSession, version: int, note: str) -> int:
    """One audited operation: exactly one version stays active."""
    target = (
        await session.execute(
            select(RoutingVersion).where(RoutingVersion.version == version)
        )
    ).scalar_one_or_none()
    if target is None:
        raise ValueError(f"unknown routing version {version}")
    current = await get_active(session)
    for row in (
        await session.execute(select(RoutingVersion).where(RoutingVersion.active.is_(True)))
    ).scalars().all():
        row.active = False
    target.active = True
    target.activated_at = datetime.datetime.now(datetime.UTC)
    from_version = current.version if current else None
    target.activated_note = f"switch {from_version} -> {version}: {note}"
    await session.commit()
    return target.version


async def rollback(session: AsyncSession, note: str = "rollback") -> int:
    current = await get_active(session)
    if current is None:
        raise ValueError("no active routing version")
    previous = (
        await session.execute(
            select(RoutingVersion)
            .where(RoutingVersion.version < current.version)
            .order_by(RoutingVersion.version.desc()).limit(1)
        )
    ).scalar_one_or_none()
    if previous is None:
        raise ValueError("no previous version to roll back to")
    return await switch_version(session, previous.version, note)

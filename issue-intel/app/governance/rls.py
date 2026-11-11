"""Row-level-security context: SET LOCAL inside one transaction per request."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import create_session_factory
from app.governance.entitlements import Entitlements, resolve_entitlements


@asynccontextmanager
async def rls_session(ent: Entitlements) -> AsyncIterator[AsyncSession]:
    factory = create_session_factory()
    async with factory() as session:
        async with session.begin():
            await session.execute(
                text("SET LOCAL app.modules = :v"), {"v": ",".join(sorted(ent.modules))}
            )
            await session.execute(
                text("SET LOCAL app.departments = :v"),
                {"v": ",".join(sorted(ent.departments))},
            )
            await session.execute(
                text("SET LOCAL app.max_restriction = :v"), {"v": str(ent.max_restriction)}
            )
            yield session


@asynccontextmanager
async def service_session() -> AsyncIterator[AsyncSession]:
    """Full-SE session for compute-once runs and ingestion.

    Uses session-level SET (not SET LOCAL) so the context survives the
    per-stage commits; RESET on exit.
    """
    ent = Entitlements.service()
    factory = create_session_factory()
    async with factory() as session:
        await session.execute(
            text("SET app.modules = :v"), {"v": ",".join(sorted(ent.modules))}
        )
        await session.execute(
            text("SET app.departments = :v"), {"v": ",".join(sorted(ent.departments))}
        )
        await session.execute(
            text("SET app.max_restriction = :v"), {"v": str(ent.max_restriction)}
        )
        try:
            yield session
        finally:
            await session.execute(text("RESET app.modules"))
            await session.execute(text("RESET app.departments"))
            await session.execute(text("RESET app.max_restriction"))


async def rls_session_dep(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: user id from the x-user-id header, fail closed."""
    try:
        user_id = int(request.headers.get("x-user-id", "0"))
    except ValueError:
        user_id = 0
    factory = create_session_factory()
    async with factory() as service:
        ent = await resolve_entitlements(service, user_id)
    async with rls_session(ent) as session:
        yield session

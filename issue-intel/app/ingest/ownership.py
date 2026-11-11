"""People and ownership map: who to ask now when the author has left."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g1 import Ownership, Person


async def build_ownership(
    session: AsyncSession, ownership: dict[str, str]
) -> dict[str, str]:
    """Upsert the module -> owner map. Returns module -> current owner."""
    people = {
        p.handle: p for p in (await session.execute(select(Person))).scalars().all()
    }
    resolved: dict[str, str] = {}
    for module, handle in ownership.items():
        person = people.get(handle)
        owner = handle
        if person is None or person.status == "LEFT":
            active = next(
                (p for p in people.values()
                 if p.status == "ACTIVE" and p.team == "Sustained-Engineering"),
                None,
            )
            owner = active.handle if active else handle
        existing = (
            await session.execute(
                select(Ownership).where(Ownership.scope == "module", Ownership.target == module)
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(Ownership(scope="module", target=module, owner_handle=owner))
        else:
            existing.owner_handle = owner
        resolved[module] = owner
    await session.flush()
    return resolved


async def current_owner(session: AsyncSession, module: str) -> str | None:
    row = (
        await session.execute(
            select(Ownership).where(Ownership.scope == "module", Ownership.target == module)
        )
    ).scalar_one_or_none()
    return row.owner_handle if row else None


async def redirect_if_left(session: AsyncSession, handle: str, module: str) -> str:
    person = (
        await session.execute(select(Person).where(Person.handle == handle))
    ).scalar_one_or_none()
    if person is not None and person.status == "LEFT":
        return await current_owner(session, module) or handle
    return handle

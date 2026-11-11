"""Entitlements: modules, departments, maximum restriction level per user."""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g1 import Entitlement as EntitlementRow

RESTRICTION_LEVELS = {"OPEN": 0, "SE": 1, "CUSTOMER_RESTRICTED": 2}

FULL_MODULES = {"VersionControl", "Localization", "UiState", "AssetImport"}
FULL_DEPARTMENTS = {"SE", "Support", "Partner"}


@dataclass
class Entitlements:
    modules: set[str] = field(default_factory=set)
    departments: set[str] = field(default_factory=set)
    max_restriction: int = -1  # fail closed: sees nothing

    @classmethod
    def service(cls) -> Entitlements:
        return Entitlements(set(FULL_MODULES), set(FULL_DEPARTMENTS), max_restriction=2)


def is_visible(modules: str, departments: str, restriction: int, ent: Entitlements) -> bool:
    """Pure ACL check shared by rendering and evals."""
    if restriction > ent.max_restriction:
        return False
    if not (set(modules.split(",")) & ent.modules):
        return False
    return bool(set(departments.split(",")) & ent.departments)


async def resolve_entitlements(session: AsyncSession, user_id: int) -> Entitlements:
    rows = (
        await session.execute(select(EntitlementRow).where(EntitlementRow.user_id == user_id))
    ).scalars().all()
    if not rows:
        return Entitlements()
    modules: set[str] = set()
    departments: set[str] = set()
    max_restriction = -1
    for row in rows:
        modules.update(m for m in row.modules.split(",") if m)
        departments.update(d for d in row.departments.split(",") if d)
        max_restriction = max(max_restriction, row.max_restriction)
    return Entitlements(modules, departments, max_restriction)

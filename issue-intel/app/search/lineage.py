"""Lineage expansion: duplicates, fixing change, outcome, current owner."""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingest.ownership import current_owner, redirect_if_left
from app.models.g1 import Case, Change, Link


@dataclass
class CaseLineage:
    key: str
    outcome: str
    duplicates: list[str] = field(default_factory=list)
    fixed_by: list[str] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)
    owner: str | None = None


async def expand_lineage(session: AsyncSession, case_keys: list[str]) -> dict[str, CaseLineage]:
    cases = (
        await session.execute(select(Case).where(Case.source_key.in_(case_keys)))
    ).scalars().all()
    result: dict[str, CaseLineage] = {}
    for case in cases:
        lineage = CaseLineage(key=case.source_key, outcome=case.outcome)
        links = (
            await session.execute(
                select(Link).where(Link.from_type == "case",
                                   Link.from_key == case.source_key)
            )
        ).scalars().all()
        for link in links:
            if link.kind == "DUPLICATE_OF":
                lineage.duplicates.append(link.to_key)
            elif link.kind == "FIXED_BY":
                lineage.fixed_by.append(link.to_key)
            elif link.kind == "MENTIONS":
                lineage.mentions.append(f"{link.to_type}:{link.to_key}")
        if case.fixed_change and case.fixed_change not in lineage.fixed_by:
            lineage.fixed_by.append(case.fixed_change)
        lineage.owner = await current_owner(session, case.module)
        result[case.source_key] = lineage
    return result


async def change_summary(session: AsyncSession, ref: str) -> dict[str, str]:
    change = (
        await session.execute(select(Change).where(Change.ref == ref))
    ).scalar_one_or_none()
    if change is None:
        return {"ref": ref, "missing": "true"}
    author = await redirect_if_left(session, change.author, "")
    return {
        "ref": change.ref, "repo": change.repo, "author": author,
        "files": change.files, "message": change.message,
    }

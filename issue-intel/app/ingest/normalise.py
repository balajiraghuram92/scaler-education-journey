"""Normalise raw records to ORM rows. Idempotent upserts by natural key."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.governance.entitlements import RESTRICTION_LEVELS
from app.ingest.extract import RawCase, RawChange, RawPerson, RawThread
from app.models.g1 import Acl, Case, Change, Message, Person, Thread


async def get_or_create_acl(
    session: AsyncSession, modules: str, departments: str, restriction: str
) -> Acl:
    level = RESTRICTION_LEVELS[restriction]
    existing = (
        await session.execute(
            select(Acl).where(
                Acl.modules == modules,
                Acl.departments == departments,
                Acl.restriction == level,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    acl = Acl(modules=modules, departments=departments, restriction=level, label=restriction)
    session.add(acl)
    await session.flush()
    return acl


async def upsert_case(session: AsyncSession, raw: RawCase) -> Case:
    acl = await get_or_create_acl(
        session, raw.true_module, ",".join(raw.departments), raw.restriction
    )
    existing = (
        await session.execute(
            select(Case).where(Case.source == raw.source, Case.source_key == raw.key)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    case = Case(
        source=raw.source, source_key=raw.key, module=raw.true_module,
        filed_module=raw.filed_module, title=raw.title, body=raw.body,
        version=raw.version, status=raw.status, raw_resolution=raw.resolution,
        outcome="UNKNOWN", fixed_change=raw.fixed_change,
        customer_ref=raw.customer_ref, acl_id=acl.id,
    )
    session.add(case)
    await session.flush()
    return case


async def upsert_thread(session: AsyncSession, raw: RawThread, acl_id: int) -> Thread:
    existing = (
        await session.execute(select(Thread).where(Thread.key == raw.key))
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    source = "TRACKER" if raw.case_key.startswith("TES-") else "LEGACY"
    thread = Thread(key=raw.key, case_source=source, case_key=raw.case_key, acl_id=acl_id)
    session.add(thread)
    await session.flush()
    for message in raw.messages:
        session.add(
            Message(thread_id=thread.id, seq=message.seq, author=message.author,
                    text=message.text, acl_id=acl_id)
        )
    await session.flush()
    return thread


async def upsert_change(session: AsyncSession, raw: RawChange, acl_id: int) -> Change:
    existing = (
        await session.execute(select(Change).where(Change.ref == raw.ref))
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    change = Change(
        ref=raw.ref, repo=raw.repo, author=raw.author,
        reviewers=",".join(raw.reviewers), files=",".join(raw.files),
        message=raw.message, legacy_id=raw.ref if raw.repo == "legacy-svn" else "",
        planned_seq=raw.planned_seq, acl_id=acl_id,
    )
    session.add(change)
    await session.flush()
    return change


async def upsert_person(session: AsyncSession, raw: RawPerson) -> Person:
    existing = (
        await session.execute(select(Person).where(Person.handle == raw.handle))
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    person = Person(handle=raw.handle, name=raw.name, team=raw.team, status=raw.status)
    session.add(person)
    await session.flush()
    return person

"""Crosswalk: link records across legacy, tracker and support systems.

Three passes, strongest first; every link records how it was found and a
confidence: explicit fields (1.0), ids mentioned in text (0.9), title
similarity above a high threshold (0.8).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g1 import Case, Change, Link

KEY_RE = re.compile(r"\b(LGC|TES|SUP)-\d{4}\b")
CHANGE_RE = re.compile(r"\b(SAMPLE-\d{2}|r\d{5})\b")
TITLE_SIMILARITY_THRESHOLD = 0.75


@dataclass
class FoundLink:
    from_type: str
    from_key: str
    to_type: str
    to_key: str
    kind: str
    evidence: str
    confidence: float


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2}


def title_similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


async def _add_link(session: AsyncSession, link: FoundLink) -> bool:
    existing = (
        await session.execute(
            select(Link).where(
                Link.from_type == link.from_type, Link.from_key == link.from_key,
                Link.to_type == link.to_type, Link.to_key == link.to_key,
                Link.kind == link.kind,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return False
    session.add(
        Link(from_type=link.from_type, from_key=link.from_key, to_type=link.to_type,
             to_key=link.to_key, kind=link.kind, evidence=link.evidence,
             confidence=link.confidence)
    )
    return True


async def crosswalk(session: AsyncSession) -> int:
    """Run all three passes. Returns the number of new links. Idempotent."""
    cases = (await session.execute(select(Case))).scalars().all()
    by_key = {c.source_key: c for c in cases}
    changes = {c.ref for c in (await session.execute(select(Change))).scalars().all()}
    added = 0

    # Pass 1: explicit fields.
    for case in cases:
        if case.fixed_change and case.fixed_change in changes:
            added += await _add_link(
                session, FoundLink("case", case.source_key, "change", case.fixed_change,
                                   "FIXED_BY", "explicit:fixed_change", 1.0))

    # Pass 2: ids mentioned in text.
    for case in cases:
        text = f"{case.title}\n{case.body}\n{case.raw_resolution}"
        for match in KEY_RE.findall(text):
            for other in [k for k in by_key if k.startswith(match) and k != case.source_key]:
                if other in text:
                    added += await _add_link(
                        session, FoundLink("case", case.source_key, "case", other,
                                           "MENTIONS", "text:case-key", 0.9))
        for ref in set(CHANGE_RE.findall(text)):
            if ref in changes:
                added += await _add_link(
                    session, FoundLink("case", case.source_key, "change", ref,
                                       "MENTIONS", "text:change-ref", 0.9))

    # Pass 3: title similarity above a high threshold, same module only.
    legacy = [c for c in cases if c.source == "LEGACY"]
    others = [c for c in cases if c.source != "LEGACY"]
    for case in others:
        best: Case | None = None
        best_score = 0.0
        for cand in legacy:
            if cand.module != case.module:
                continue
            score = title_similarity(case.title, cand.title)
            if score > best_score:
                best, best_score = cand, score
        if best is not None and best_score >= TITLE_SIMILARITY_THRESHOLD:
            added += await _add_link(
                session, FoundLink("case", case.source_key, "case", best.source_key,
                                   "DUPLICATE_OF", f"similarity:{best_score:.2f}", 0.8))
    await session.flush()
    return added

"""Hybrid search: full-text + vector queries fused with reciprocal rank fusion."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SearchMode = Literal["fulltext", "vector", "fused"]
RRF_K = 60
CANDIDATE_LIMIT = 30


@dataclass
class SearchHit:
    chunk_id: int
    owner_type: str
    owner_key: str
    text: str
    score: float
    source: str  # fulltext | vector | fused


async def _fulltext(session: AsyncSession, query: str) -> list[tuple[int, str, str, str]]:
    rows = (
        await session.execute(
            text(
                "SELECT id, owner_type, owner_key, text FROM chunks"
                " WHERE tsv @@ replace(plainto_tsquery('english', :q)::text, '&', '|')::tsquery"
                " ORDER BY ts_rank(tsv,"
                " replace(plainto_tsquery('english', :q)::text, '&', '|')::tsquery) DESC"
                " LIMIT :lim"
            ),
            {"q": query, "lim": CANDIDATE_LIMIT},
        )
    ).all()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


async def _vector(
    session: AsyncSession, query_vector: list[float]
) -> list[tuple[int, str, str, str]]:
    rows = (
        await session.execute(
            text(
                "SELECT id, owner_type, owner_key, text FROM chunks"
                " ORDER BY embedding <=> CAST(:v AS vector) LIMIT :lim"
            ),
            {"v": str(query_vector), "lim": CANDIDATE_LIMIT},
        )
    ).all()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def _rrf(
    ranked: list[list[tuple[int, str, str, str]]], limit: int
) -> list[tuple[int, str, str, str, float]]:
    scores: dict[int, float] = {}
    rows: dict[int, tuple[int, str, str, str]] = {}
    for listing in ranked:
        for rank, row in enumerate(listing):
            scores[row[0]] = scores.get(row[0], 0.0) + 1.0 / (RRF_K + rank + 1)
            rows.setdefault(row[0], row)
    fused = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    out: list[tuple[int, str, str, str, float]] = []
    for chunk_id, score in fused:
        r = rows[chunk_id]
        out.append((r[0], r[1], r[2], r[3], score))
    return out


async def hybrid_search(
    session: AsyncSession,
    query_text: str,
    query_vector: list[float],
    limit: int = 10,
    mode: SearchMode = "fused",
) -> list[SearchHit]:
    if mode == "fulltext":
        rows = await _fulltext(session, query_text)
        return [
            SearchHit(chunk_id=r[0], owner_type=r[1], owner_key=r[2], text=r[3],
                      score=1.0 / (i + 1), source="fulltext")
            for i, r in enumerate(rows[:limit])
        ]
    if mode == "vector":
        rows = await _vector(session, query_vector)
        return [
            SearchHit(chunk_id=r[0], owner_type=r[1], owner_key=r[2], text=r[3],
                      score=1.0 / (i + 1), source="vector")
            for i, r in enumerate(rows[:limit])
        ]
    fulltext = await _fulltext(session, query_text)
    vector = await _vector(session, query_vector)
    return [
        SearchHit(chunk_id=r[0], owner_type=r[1], owner_key=r[2], text=r[3],
                  score=r[4], source="fused")
        for r in _rrf([fulltext, vector], limit)
    ]

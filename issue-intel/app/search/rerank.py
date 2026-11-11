"""Rerank the top candidates with the relevance task. Malformed model JSON
keeps the candidate at score 0.0 (fail open for recall; RLS already filtered).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.search.hybrid import SearchHit

SYSTEM = (
    "Judge whether the candidate helps answer the query. "
    'Reply with JSON only: {"relevant": true|false, "score": 0.0-1.0}.'
)


@dataclass
class RerankedHit:
    hit: SearchHit
    score: float


def parse_relevance(text: str) -> tuple[bool, float]:
    try:
        payload = json.loads(text)
        return bool(payload.get("relevant", False)), float(payload.get("score", 0.0))
    except (ValueError, TypeError):
        return True, 0.0


async def rerank(
    gateway: ModelGateway, query: str, candidates: list[SearchHit],
    run_id: str | None = None,
) -> list[RerankedHit]:
    scored: list[RerankedHit] = []
    for cand in candidates:
        result = await gateway.complete(
            TaskType.RELEVANCE, system=SYSTEM, user=f"Query: {query}",
            data={"candidate": cand.text}, run_id=run_id,
        )
        relevant, score = parse_relevance(result.text)
        if relevant:
            scored.append(RerankedHit(hit=cand, score=score))
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored

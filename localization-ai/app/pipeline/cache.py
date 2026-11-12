"""Semantic-cache stage (pgvector cosine search over past translations).

Inputs: a DB connection, an embedding provider, a producer callback that
translates on a miss, plus project/locale/source scoping and the similarity
threshold (default 0.95: similarity at or above is a hit).

Outputs: a CachedOutcome with the translation, whether it was a cache hit,
token counts (chat + embedding), latency, computed cost, and fallback flag.

Failure behaviour: embedding failures bypass the cache (the producer still
runs; nothing is stored). Lookup/store SQL errors propagate to the caller,
which owns the transaction.
"""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import psycopg

from app.pipeline.cost import Pricing, embedding_cost_usd
from app.providers.base import EmbeddingProvider

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Produced:
    """What the producer made on a cache miss."""

    translation: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    fallback: bool = False


@dataclass(frozen=True)
class CachedOutcome:
    translation: str
    cache_hit: bool
    input_tokens: int = 0
    output_tokens: int = 0
    embedding_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    fallback: bool = False
    details: dict[str, str] = field(default_factory=dict)


Producer = Callable[[], Awaitable[Produced]]


def vector_literal(vector: list[float]) -> str:
    """Serialize a vector to pgvector text format (driver-independent)."""
    return "[" + ",".join(repr(float(v)) for v in vector) + "]"


async def translate_with_cache(
    conn: psycopg.AsyncConnection,
    embed: EmbeddingProvider,
    producer: Producer,
    *,
    project_id: int,
    locale_code: str,
    source_text: str,
    threshold: float = 0.95,
    expected_dimensions: int = 384,
    pricing: Pricing | None = None,
) -> CachedOutcome:
    """Translate through the semantic cache: hit returns the cached row (and
    bumps its hit count); miss runs the producer, then stores the result."""
    rates = pricing or Pricing()
    try:
        embedded = await embed.embed([source_text])
    except Exception as exc:
        logger.warning("cache bypassed: embedding failed (%s)", exc)
        produced = await producer()
        return CachedOutcome(
            translation=produced.translation,
            cache_hit=False,
            input_tokens=produced.input_tokens,
            output_tokens=produced.output_tokens,
            latency_ms=produced.latency_ms,
            cost_usd=produced.cost_usd,
            fallback=produced.fallback,
            details={"cache": f"bypassed: embedding failed ({exc})"},
        )
    vector = embedded[0].vector
    if len(vector) != expected_dimensions:
        raise ValueError(f"embedding has {len(vector)} dimensions, expected {expected_dimensions}")
    embed_cost = embedding_cost_usd(embedded[0].tokens, per_1k_usd=rates.embedding_per_1k_usd)
    literal = vector_literal(vector)

    cur = await conn.execute(
        "SELECT id, cached_translation, source_embedding <=> %s::vector AS distance"
        " FROM localization_translation_cache_entries"
        " WHERE project_id = %s AND locale_code = %s AND source_embedding IS NOT NULL"
        " ORDER BY source_embedding <=> %s::vector LIMIT 1",
        (literal, project_id, locale_code, literal),
    )
    row = await cur.fetchone()
    if row is not None and (1.0 - float(row[2])) >= threshold:
        await conn.execute(
            "UPDATE localization_translation_cache_entries SET hit_count = hit_count + 1, last_hit_at = now()"
            " WHERE id = %s",
            (row[0],),
        )
        return CachedOutcome(
            translation=row[1],
            cache_hit=True,
            embedding_tokens=embedded[0].tokens,
            latency_ms=embedded[0].latency_ms,
            cost_usd=embed_cost,
        )

    produced = await producer()
    await conn.execute(
        "INSERT INTO localization_translation_cache_entries"
        " (project_id, locale_code, source_text, source_embedding, cached_translation, hit_count, created_at)"
        " VALUES (%s, %s, %s, %s::vector, %s, 0, now())",
        (project_id, locale_code, source_text, literal, produced.translation),
    )
    return CachedOutcome(
        translation=produced.translation,
        cache_hit=False,
        input_tokens=produced.input_tokens,
        output_tokens=produced.output_tokens,
        embedding_tokens=embedded[0].tokens,
        latency_ms=embedded[0].latency_ms + produced.latency_ms,
        cost_usd=embed_cost + produced.cost_usd,
        fallback=produced.fallback,
    )

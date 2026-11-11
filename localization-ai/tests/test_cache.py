"""Semantic-cache tests with scripted embeddings (the hash-based fake makes all
distinct texts near-orthogonal, so separation is tested with exact vectors).

NEAR_DUPLICATE_PAIRS must hit; CONFUSABLE_PAIRS (look similar, mean
something different) must not. The scripted vectors below separate at the
0.95 default by construction; the skipped real-embedding test reports the
threshold at which a real model separates them.
"""

import asyncio
import functools
import math
import os

import psycopg
import pytest

from app.pipeline import cache
from app.pipeline.cache import Produced
from app.providers.base import EmbeddingResult
from app.providers.openai_compat import OpenAICompatEmbeddingProvider

DIMS = 384

# (stored source, query source): same meaning, tiny surface difference.
NEAR_DUPLICATE_PAIRS = [
    ("Turn left ahead", "Turn left ahead!"),
    ("Low fuel warning", "Low fuel warning."),
    ("Door ajar", "Door ajar!"),
    ("Cabin temperature", "cabin temperature"),
]

# (stored source, query source): similar surface, different meaning.
CONFUSABLE_PAIRS = [
    ("Turn left", "Turn right"),
    ("Door open", "Door closed"),
    ("Front left tire", "Front right tire"),
    ("Resume media playback", "Pause audio playback"),
]


def vec_at_cosine(similarity: float, axis: int = 0, dims: int = DIMS) -> list[float]:
    """Unit vector at exactly `similarity` cosine to e1 (for scripted tests).

    Distinct `axis` values spread the remainder over orthogonal dimensions,
    so same-similarity vectors on different axes stay far apart.
    """
    rest = math.sqrt(max(0.0, 1.0 - similarity * similarity))
    vector = [0.0] * dims
    vector[0] = similarity
    vector[1 + axis] = rest
    return vector


class ScriptedEmbeddings:
    """EmbeddingProvider stub returning hand-set vectors per text."""

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self.name = "scripted-test"
        self.dimensions = DIMS
        self._vectors = vectors
        self.calls: list[str] = []

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        results = []
        for text in texts:
            self.calls.append(text)
            results.append(EmbeddingResult(vector=self._vectors[text], tokens=2, latency_ms=1))
        return results

    async def close(self) -> None:
        pass


def _conn_id(conninfo: str, slug: str = "c") -> int:
    with psycopg.connect(conninfo) as conn:
        cur = conn.execute(
            "INSERT INTO localization_projects (slug, name) VALUES (%s, 'C') RETURNING id", (slug,)
        )
        row = cur.fetchone()
        assert row is not None
        conn.commit()
        return row[0]


async def _run(conninfo: str, project_id: int, embed, producer, **kwargs):
    conn = await psycopg.AsyncConnection.connect(conninfo)
    try:
        outcome = await cache.translate_with_cache(
            conn, embed, producer, project_id=project_id, locale_code="de-DE", **kwargs
        )
        await conn.commit()
        return outcome
    finally:
        await conn.close()


def _producer(text: str, calls: list[str]):
    async def produce() -> Produced:
        calls.append(text)
        return Produced(translation=text, input_tokens=10, output_tokens=5, latency_ms=3, cost_usd=0.01)

    return produce


def test_miss_stores_then_identical_query_hits(fresh_db):
    project_id = _conn_id(fresh_db)
    embed = ScriptedEmbeddings({"Turn left": vec_at_cosine(1.0)})
    run = functools.partial(_run, fresh_db, project_id, embed)
    calls: list[str] = []
    miss = asyncio.run(run(_producer("Links abbiegen", calls), source_text="Turn left", threshold=0.95))
    assert miss.cache_hit is False
    assert miss.translation == "Links abbiegen"
    assert (miss.input_tokens, miss.output_tokens, miss.embedding_tokens) == (10, 5, 2)
    assert miss.latency_ms == 4  # embed (1) + producer (3)
    assert miss.cost_usd == 0.01  # zero embedding rate in default Pricing

    hit = asyncio.run(run(_producer("OTHER", calls), source_text="Turn left", threshold=0.95))
    assert hit.cache_hit is True
    assert hit.translation == "Links abbiegen"
    assert calls == ["Links abbiegen"]  # producer ran once: the hit skipped it
    assert (hit.input_tokens, hit.output_tokens) == (0, 0)

    with psycopg.connect(fresh_db) as conn:
        row = conn.execute("SELECT hit_count, last_hit_at FROM localization_translation_cache_entries").fetchone()
    assert row is not None and row[0] == 1 and row[1] is not None


def test_near_duplicates_hit_and_confusables_miss(fresh_db):
    project_id = _conn_id(fresh_db)
    stored = [s for s, _ in NEAR_DUPLICATE_PAIRS] + [s for s, _ in CONFUSABLE_PAIRS]
    queries = {q: vec_at_cosine(0.97) for _, q in NEAR_DUPLICATE_PAIRS}
    # Confusables share 0.42 with e1 but sit on distinct axes (mutual cosine
    # 0.42^2), so stored confusables never match each other.
    for i, (_, q) in enumerate(CONFUSABLE_PAIRS):
        queries[q] = vec_at_cosine(0.42, axis=i)
    vectors = {s: vec_at_cosine(1.0) for s in stored} | queries
    embed = ScriptedEmbeddings(vectors)
    run = functools.partial(_run, fresh_db, project_id, embed)
    for source in stored:
        asyncio.run(run(_producer(f"T:{source}", []), source_text=source, threshold=0.95))
    for _, query in NEAR_DUPLICATE_PAIRS:
        # 0.97 vs e1: cosine to the stored row is 0.97 >= 0.95.
        outcome = asyncio.run(run(_producer("OTHER", []), source_text=query, threshold=0.95))
        assert outcome.cache_hit is True, query
    for _, query in CONFUSABLE_PAIRS:
        # 0.42 vs e1: below threshold against every stored row.
        outcome = asyncio.run(run(_producer(f"T:{query}", []), source_text=query, threshold=0.95))
        assert outcome.cache_hit is False, query


def test_threshold_is_respected(fresh_db):
    project_id = _conn_id(fresh_db)
    embed = ScriptedEmbeddings({"A": vec_at_cosine(1.0), "B": vec_at_cosine(0.97)})
    run = functools.partial(_run, fresh_db, project_id, embed)
    asyncio.run(run(_producer("T:A", []), source_text="A", threshold=0.95))
    # 0.97 >= 0.95 hits, but 0.97 < 0.99 misses.
    hit = asyncio.run(run(_producer("X", []), source_text="B", threshold=0.95))
    assert hit.cache_hit is True
    miss = asyncio.run(run(_producer("Y", []), source_text="B", threshold=0.99))
    assert miss.cache_hit is False


def test_cache_is_scoped_to_project_and_locale(fresh_db):
    project_id = _conn_id(fresh_db)
    other_id = _conn_id(fresh_db, slug="d")
    embed = ScriptedEmbeddings({"Same": vec_at_cosine(1.0)})

    async def go(conn, pid: int, locale: str):
        return await cache.translate_with_cache(
            conn, embed, _producer("T", []), project_id=pid, locale_code=locale, source_text="Same")

    async def scenario():
        conn = await psycopg.AsyncConnection.connect(fresh_db)
        try:
            miss = await go(conn, project_id, "de-DE")
            same_project_other_locale = await go(conn, project_id, "fr-FR")
            other_project = await go(conn, other_id, "de-DE")
            await conn.commit()
            return miss, same_project_other_locale, other_project
        finally:
            await conn.close()

    miss, other_locale, other_project = asyncio.run(scenario())
    assert (miss.cache_hit, other_locale.cache_hit, other_project.cache_hit) == (False, False, False)


def test_dimension_mismatch_raises(fresh_db):
    project_id = _conn_id(fresh_db)
    embed = ScriptedEmbeddings({"A": [1.0, 0.0]})
    run = functools.partial(_run, fresh_db, project_id, embed)
    with pytest.raises(ValueError, match="dimensions"):
        asyncio.run(run(_producer("T", []), source_text="A", threshold=0.95, expected_dimensions=DIMS))


def test_embedding_failure_bypasses_cache(fresh_db):
    project_id = _conn_id(fresh_db)

    class Failing:
        name = "failing-test"
        dimensions = DIMS

        async def embed(self, texts: list[str]):
            raise RuntimeError("model down")

        async def close(self) -> None:
            pass

    run = functools.partial(_run, fresh_db, project_id, Failing())
    outcome = asyncio.run(run(_producer("T", []), source_text="A", threshold=0.95))
    assert outcome.cache_hit is False
    assert outcome.translation == "T"
    assert "bypassed" in outcome.details["cache"]
    with psycopg.connect(fresh_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM localization_translation_cache_entries").fetchone() == (0,)


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


@pytest.mark.skipif(os.environ.get("LOCAI_REAL_EMBEDDINGS") != "1", reason="needs a real embedding model")
def test_report_real_embedding_separation():
    """Report the threshold at which a real model separates the pair sets.

    Run with LOCAI_REAL_EMBEDDINGS=1 (+ LOCAI_REAL_EMBEDDING_* env). Prints
    per-pair cosines and fails only when the sets do not separate at all.
    """
    async def go():
        provider = OpenAICompatEmbeddingProvider(
            base_url=os.environ.get("LOCAI_REAL_EMBEDDING_BASE_URL", "http://localhost:8001/v1"),
            api_key=os.environ.get("LOCAI_REAL_EMBEDDING_API_KEY", ""),
            model=os.environ["LOCAI_REAL_EMBEDDING_MODEL"],
            dimensions=int(os.environ.get("LOCAI_REAL_EMBEDDING_DIMENSIONS", "384")),
            timeout_seconds=120.0,
        )
        try:
            pairs = NEAR_DUPLICATE_PAIRS + CONFUSABLE_PAIRS
            texts = [t for p in pairs for t in p]
            vectors = [r.vector for r in await provider.embed(texts)]
            by_text = dict(zip(texts, vectors, strict=True))
            near = [_cosine(by_text[a], by_text[b]) for a, b in NEAR_DUPLICATE_PAIRS]
            conf = [_cosine(by_text[a], by_text[b]) for a, b in CONFUSABLE_PAIRS]
            return near, conf
        finally:
            await provider.close()

    near, conf = asyncio.run(go())
    for (a, b), sim in zip(NEAR_DUPLICATE_PAIRS + CONFUSABLE_PAIRS, near + conf, strict=True):
        print(f"{sim:.4f}  {a!r}  <->  {b!r}")
    worst_near, best_conf = min(near), max(conf)
    print(f"min near-duplicate: {worst_near:.4f}; max confusable: {best_conf:.4f}")
    assert worst_near > best_conf, "pair sets do not separate with this embedding model"
    print(f"suggested threshold midpoint: {(worst_near + best_conf) / 2:.4f}")

"""End-to-end runs of the LA3 configs against the test database with scripted
fakes. Metric expectations are literals; token/cost expectations derive from
the providers' recorded calls (deterministic, still verifying the plumbing).
"""

import asyncio
import json

import psycopg

from app.evals.runner import run_eval
from app.pipeline.cost import Pricing
from app.pipeline.registry import PipelineContext
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider, count_tokens

OPT_1 = json.dumps({"optimized_translation": "Links abbiegen"})
OPT_2 = json.dumps({"optimized_translation": "HUD {count}"})


def _judge(score: int) -> str:
    assert score % 4 == 0
    dim = {"score": score // 4, "justification": "scripted"}
    return json.dumps({"accuracy": dim, "fluency": dim, "terminology": dim, "tone": dim, "flagged_issues": []})


def _run_all(conninfo: str, chat: FakeChatProvider, embed: FakeEmbeddingProvider, config: str, pricing: Pricing):
    async def go():
        conn = await psycopg.AsyncConnection.connect(conninfo)
        try:
            ctx = PipelineContext(chat=chat, embed=embed, project_slug="test-proj", pricing=pricing)
            summary = await run_eval(conn, project_slug="test-proj", pipeline_config=config, ctx=ctx)
            await conn.commit()
            return summary
        finally:
            await conn.close()

    return asyncio.run(go())


def _chat_tokens(chat: FakeChatProvider, script: list[str]) -> tuple[int, int]:
    assert len(chat.calls) == len(script)
    inputs = sum(count_tokens("\n".join(m.content for m in call)) for call in chat.calls)
    outputs = sum(count_tokens(text) for text in script)
    return inputs, outputs


def test_legacy_optimize_run(seeded_project_id):
    conninfo, _ = seeded_project_id
    script = [OPT_1, _judge(80), OPT_2, _judge(100)]
    chat, embed = FakeChatProvider(responses=list(script)), FakeEmbeddingProvider()
    summary = _run_all(conninfo, chat, embed, "legacy+optimize", Pricing())

    assert summary.case_count == 2
    assert summary.avg_qps_score == 90.0
    assert summary.glossary_adherence_rate == 1.0
    assert summary.placeholder_preservation_rate == 1.0
    assert summary.cache_hit_rate == 0.0
    assert summary.avg_latency_ms is not None and summary.avg_latency_ms >= 0
    assert summary.total_cost_usd == 0.0
    assert summary.fallback_count == 0
    assert summary.prompt_version == "mt-optimize-v1+qps-judge-v1"
    chat_in, chat_out = _chat_tokens(chat, script)
    assert summary.tokens_used == chat_in + chat_out
    # Ungrounded: the optimize prompt carries no glossary block entries.
    assert '"Turn left" must be rendered as' not in chat.calls[0][0].content


def test_legacy_optimize_glossary_run_is_grounded(seeded_project_id):
    conninfo, _ = seeded_project_id
    script = [OPT_1, _judge(80), OPT_2, _judge(100)]
    chat, embed = FakeChatProvider(responses=list(script)), FakeEmbeddingProvider()
    summary = _run_all(conninfo, chat, embed, "legacy+optimize+glossary", Pricing())

    assert summary.avg_qps_score == 90.0
    assert summary.fallback_count == 0
    assert '"Turn left" must be rendered as "Links abbiegen"' in chat.calls[0][0].content
    assert '"HUD" must be rendered as "HUD"' in chat.calls[2][0].content


def test_legacy_optimize_glossary_cache_miss_then_hit(seeded_project_id):
    conninfo, _ = seeded_project_id
    pricing = Pricing(chat_in_per_1k_usd=1000.0, chat_out_per_1k_usd=2000.0, embedding_per_1k_usd=500.0)

    script1 = [OPT_1, _judge(80), OPT_2, _judge(100)]
    chat1, embed1 = FakeChatProvider(responses=list(script1)), FakeEmbeddingProvider()
    first = _run_all(conninfo, chat1, embed1, "legacy+optimize+glossary+cache", pricing)
    assert first.cache_hit_rate == 0.0
    # The 1 is the fake embedding call; the optimize step is measured wall-clock time.
    assert first.avg_latency_ms is not None and first.avg_latency_ms >= 1
    assert first.fallback_count == 0
    chat_in, chat_out = _chat_tokens(chat1, script1)
    embed_tokens = sum(count_tokens(t) for t in embed1.calls)
    assert embed_tokens > 0
    assert first.tokens_used == chat_in + chat_out + embed_tokens
    assert first.total_cost_usd == chat_in / 1000 * 1000.0 + chat_out / 1000 * 2000.0 + embed_tokens / 1000 * 500.0

    # Second run: both cases hit the cache, so no optimize calls happen —
    # only the two judge calls remain in the script.
    script2 = [_judge(80), _judge(100)]
    chat2, embed2 = FakeChatProvider(responses=list(script2)), FakeEmbeddingProvider()
    second = _run_all(conninfo, chat2, embed2, "legacy+optimize+glossary+cache", Pricing())
    assert second.cache_hit_rate == 1.0
    assert second.avg_latency_ms == 1  # embed lookup only
    assert len(chat2.calls) == 2  # judges only; optimize never ran
    assert second.avg_qps_score == 90.0


def test_legacy_only_now_carries_judge_scores(seeded_project_id):
    conninfo, _ = seeded_project_id
    script = [_judge(20), _judge(40)]
    chat, embed = FakeChatProvider(responses=list(script)), FakeEmbeddingProvider()
    summary = _run_all(conninfo, chat, embed, "legacy-only", Pricing())

    assert summary.avg_qps_score == 30.0
    assert summary.prompt_version == "none"
    assert summary.fallback_count == 0
    assert len(chat.calls) == 2  # pipeline made no calls; judges only

    with psycopg.connect(conninfo) as conn:
        rows = conn.execute(
            "SELECT produced_translation, qps_score FROM localization_eval_case_results"
            " ORDER BY eval_golden_case_id"
        ).fetchall()
    assert rows == [("Turn left", 20), ("HUD {count}", 40)]

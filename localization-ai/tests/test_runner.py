"""Whole-run test: legacy-only eval against a test database, checked against
hand-computed literal expectations (see the seeded_project_id fixture)."""

import asyncio

import psycopg
import pytest

from app.evals.runner import EmptyGoldenSetError, UnknownProjectError, run_eval
from app.pipeline.registry import PipelineContext, UnknownPipelineError
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider


def _run(conninfo: str, **kwargs):
    async def go():
        conn = await psycopg.AsyncConnection.connect(conninfo)
        try:
            ctx = PipelineContext(chat=FakeChatProvider(), embed=FakeEmbeddingProvider(), project_slug="test-proj")
            summary = await run_eval(conn, project_slug="test-proj", pipeline_config="legacy-only", ctx=ctx, **kwargs)
            await conn.commit()
            return summary
        finally:
            await conn.close()

    return asyncio.run(go())


def test_legacy_only_run_matches_hand_computed_expectations(seeded_project_id):
    conninfo, project_id = seeded_project_id
    summary = _run(conninfo)

    # Case 1 ("Turn left" -> echo "Turn left"): glossary applicable
    # ("Turn left"->"Links abbiegen") but unmet -> False; no placeholders
    # -> excluded. Case 2 ("HUD {count}" -> echo): glossary met -> True,
    # placeholder preserved -> True.
    assert summary.pipeline_config == "legacy-only"
    assert summary.case_count == 2
    assert summary.avg_comet_kiwi is None  # no scorer in this run
    assert summary.avg_qps_score is None  # no judge until LA3
    assert summary.glossary_adherence_rate == 0.5
    assert summary.placeholder_preservation_rate == 1.0
    assert summary.cache_hit_rate == 0.0  # legacy-only never consults a cache
    assert summary.avg_latency_ms == 0
    assert summary.total_cost_usd == 0.0

    with psycopg.connect(conninfo) as conn:
        run_rows = conn.execute(
            "SELECT project_id, pipeline_config, avg_comet_kiwi, avg_qps_score,"
            " glossary_adherence_rate, placeholder_preservation_rate, cache_hit_rate,"
            " avg_latency_ms, total_cost_usd"
            " FROM localization_eval_runs"
        ).fetchall()
        assert len(run_rows) == 1
        assert run_rows[0] == (project_id, "legacy-only", None, None, 0.5, 1.0, 0.0, 0, 0.0)

        case_rows = conn.execute(
            "SELECT produced_translation, comet_kiwi_score, qps_score,"
            " glossary_adherence_ok, placeholder_preserved_ok, latency_ms, cache_hit, cost_usd"
            " FROM localization_eval_case_results ORDER BY eval_golden_case_id"
        ).fetchall()
        assert case_rows == [
            ("Turn left", None, None, False, None, 0, False, 0.0),
            ("HUD {count}", None, None, True, True, 0, False, 0.0),
        ]


def test_run_eval_unknown_project(seeded_project_id):
    conninfo, _ = seeded_project_id

    async def go():
        conn = await psycopg.AsyncConnection.connect(conninfo)
        try:
            ctx = PipelineContext(chat=FakeChatProvider(), embed=FakeEmbeddingProvider())
            with pytest.raises(UnknownProjectError):
                await run_eval(conn, project_slug="nope", pipeline_config="legacy-only", ctx=ctx)
        finally:
            await conn.close()

    asyncio.run(go())


def test_run_eval_unknown_pipeline_lists_available(seeded_project_id):
    conninfo, _ = seeded_project_id

    async def go():
        conn = await psycopg.AsyncConnection.connect(conninfo)
        try:
            ctx = PipelineContext(chat=FakeChatProvider(), embed=FakeEmbeddingProvider())
            with pytest.raises(UnknownPipelineError, match="legacy-only"):
                await run_eval(conn, project_slug="test-proj", pipeline_config="nope", ctx=ctx)
        finally:
            await conn.close()

    asyncio.run(go())


def test_run_eval_empty_golden_set(fresh_db):
    with psycopg.connect(fresh_db) as conn:
        conn.execute("INSERT INTO localization_projects (slug, name) VALUES ('empty', 'Empty')")
        conn.commit()

    async def go():
        conn = await psycopg.AsyncConnection.connect(fresh_db)
        try:
            ctx = PipelineContext(chat=FakeChatProvider(), embed=FakeEmbeddingProvider())
            with pytest.raises(EmptyGoldenSetError):
                await run_eval(conn, project_slug="empty", pipeline_config="legacy-only", ctx=ctx)
        finally:
            await conn.close()

    asyncio.run(go())

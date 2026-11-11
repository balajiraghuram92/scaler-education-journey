"""Metric runner: run every golden case through a pipeline config, judge each
produced translation, compute the metrics, and write one eval-run row plus
one case-result row per case.

Per-case latency is the pipeline's production latency (judge overhead is
excluded); judge tokens and cost ARE included in the run totals. This module
never commits: the caller (router, CLI, tests) commits after a successful run.
"""

from dataclasses import dataclass, replace

import psycopg

from app.db import fetch_glossary_terms, fetch_golden_cases, fetch_project
from app.evals import metrics
from app.evals.comet import CometKiwiScorer
from app.pipeline import qps
from app.pipeline.cost import Pricing
from app.pipeline.registry import CaseInput, PipelineContext, get_pipeline, prompt_version_for


class UnknownProjectError(ValueError):
    """Raised when the project slug matches no project row."""


class EmptyGoldenSetError(ValueError):
    """Raised when the project has no golden cases to run."""


@dataclass(frozen=True)
class EvalRunSummary:
    eval_run_id: int
    pipeline_config: str
    case_count: int
    avg_comet_kiwi: float | None
    avg_qps_score: float | None
    glossary_adherence_rate: float | None
    placeholder_preservation_rate: float | None
    cache_hit_rate: float | None
    avg_latency_ms: int | None
    total_cost_usd: float
    tokens_used: int
    fallback_count: int
    prompt_version: str


async def run_eval(
    conn: psycopg.AsyncConnection,
    *,
    project_slug: str,
    pipeline_config: str,
    ctx: PipelineContext,
    comet: CometKiwiScorer | None = None,
) -> EvalRunSummary:
    project = await fetch_project(conn, project_slug)
    if project is None:
        raise UnknownProjectError(f"unknown project slug {project_slug!r}")
    pipeline = get_pipeline(pipeline_config)
    cases = await fetch_golden_cases(conn, project.id)
    if not cases:
        raise EmptyGoldenSetError(f"project {project_slug!r} has no golden cases")
    glossary = await fetch_glossary_terms(conn, project.id)
    pricing = ctx.pricing or Pricing()
    # The runner's own connection/row: cached configs share this transaction.
    ctx = replace(ctx, conn=conn, project_id=project.id)

    produced: list[str] = []
    qps_scores: list[int | None] = []
    latencies: list[int] = []
    costs: list[float] = []
    token_totals: list[int] = []
    fallbacks: list[bool] = []
    cache_hits: list[bool] = []
    glossary_flags: list[bool | None] = []
    placeholder_flags: list[bool | None] = []

    for case in cases:
        terms = [(t.source_term, t.target_term) for t in glossary if t.locale_code == case.locale_code]
        output = await pipeline(
            CaseInput(
                source_text=case.source_text,
                locale_code=case.locale_code,
                gold_translation=case.gold_translation,
                category=case.category,
                glossary_terms=tuple(terms),
            ),
            ctx,
        )
        judged = await qps.score(
            ctx.chat,
            source_text=case.source_text,
            target_text=output.produced_translation,
            locale_code=case.locale_code,
            pricing=pricing,
        )
        produced.append(output.produced_translation)
        qps_scores.append(judged.score)
        latencies.append(output.latency_ms)
        costs.append(output.cost_usd + judged.cost_usd)
        case_tokens = (
            output.input_tokens + output.output_tokens + output.embedding_tokens + judged.input_tokens
            + judged.output_tokens
        )
        token_totals.append(case_tokens)
        fallbacks.append(output.fallback or judged.fallback)
        cache_hits.append(output.cache_hit)
        glossary_flags.append(metrics.glossary_adherence_ok(case.source_text, output.produced_translation, terms))
        placeholder_flags.append(metrics.placeholder_preserved_ok(case.source_text, output.produced_translation))

    comet_scores = comet.score_batch([c.source_text for c in cases], produced) if comet is not None else [None] * len(cases)

    avg_latency = metrics.mean(latencies)
    avg_comet_kiwi = metrics.mean(comet_scores)
    avg_qps_score = metrics.mean(qps_scores)
    glossary_adherence_rate = metrics.rate(glossary_flags)
    placeholder_preservation_rate = metrics.rate(placeholder_flags)
    cache_hit_rate = metrics.rate(cache_hits)
    avg_latency_ms = int(avg_latency) if avg_latency is not None else None
    total_cost_usd = metrics.total(costs)

    cur = await conn.execute(
        "INSERT INTO localization_eval_runs"
        " (project_id, pipeline_config, run_at, avg_comet_kiwi, avg_qps_score,"
        " glossary_adherence_rate, placeholder_preservation_rate, cache_hit_rate,"
        " avg_latency_ms, total_cost_usd)"
        " VALUES (%s, %s, now(), %s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (
            project.id,
            pipeline_config,
            avg_comet_kiwi,
            avg_qps_score,
            glossary_adherence_rate,
            placeholder_preservation_rate,
            cache_hit_rate,
            avg_latency_ms,
            total_cost_usd,
        ),
    )
    row = await cur.fetchone()
    assert row is not None
    run_id = row[0]

    for case, text, comet_score, qps_score, latency, cost, hit, g_ok, p_ok in zip(
        cases, produced, comet_scores, qps_scores, latencies, costs, cache_hits, glossary_flags, placeholder_flags,
        strict=True,
    ):
        await conn.execute(
            "INSERT INTO localization_eval_case_results"
            " (eval_run_id, eval_golden_case_id, produced_translation, comet_kiwi_score,"
            " qps_score, glossary_adherence_ok, placeholder_preserved_ok, latency_ms,"
            " cache_hit, cost_usd)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (run_id, case.id, text, comet_score, qps_score, g_ok, p_ok, latency, hit, cost),
        )

    return EvalRunSummary(
        eval_run_id=run_id,
        pipeline_config=pipeline_config,
        case_count=len(cases),
        avg_comet_kiwi=avg_comet_kiwi,
        avg_qps_score=avg_qps_score,
        glossary_adherence_rate=glossary_adherence_rate,
        placeholder_preservation_rate=placeholder_preservation_rate,
        cache_hit_rate=cache_hit_rate,
        avg_latency_ms=avg_latency_ms,
        total_cost_usd=total_cost_usd,
        tokens_used=sum(token_totals),
        fallback_count=sum(fallbacks),
        prompt_version=prompt_version_for(pipeline_config),
    )

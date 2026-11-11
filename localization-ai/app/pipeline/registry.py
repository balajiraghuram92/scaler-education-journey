"""Pipeline-config registry: maps a PipelineConfig name to its case function.

LA2 registered only ``legacy-only``. LA3 adds ``legacy+optimize``,
``legacy+optimize+glossary`` and ``legacy+optimize+glossary+cache``.

Eval-harness limitation, stated plainly: golden cases carry no raw MT and
this service has no MT provider, so every ``legacy*`` config feeds the
source text to MT Optimize in place of raw MT. With a real Legacy MT stage
upstream (the .NET workflow), raw MT is supplied instead.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import psycopg

from app.pipeline import cache, mt_optimize
from app.pipeline.cost import Pricing
from app.pipeline.prompts import MT_OPTIMIZE_PROMPT_VERSION, QPS_PROMPT_VERSION
from app.providers.base import ChatProvider, EmbeddingProvider


@dataclass(frozen=True)
class CaseInput:
    """One golden case as the pipeline sees it (gold is for metrics only)."""

    source_text: str
    locale_code: str
    gold_translation: str
    category: str
    raw_mt_text: str | None = None
    glossary_terms: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CaseOutput:
    """One pipeline verdict. Tokens, latency, cost and cache_hit feed the
    eval aggregates; fallback is true when a degraded path was taken."""

    produced_translation: str
    input_tokens: int = 0
    output_tokens: int = 0
    embedding_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    cache_hit: bool = False
    fallback: bool = False
    details: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineContext:
    """Shared handles every pipeline function may use."""

    chat: ChatProvider
    embed: EmbeddingProvider
    project_slug: str = ""
    conn: psycopg.AsyncConnection | None = None
    project_id: int | None = None
    cache_threshold: float = 0.95
    embedding_dimensions: int = 384
    pricing: Pricing | None = None


PipelineFn = Callable[[CaseInput, PipelineContext], Awaitable[CaseOutput]]

PIPELINE_CONFIGS: dict[str, PipelineFn] = {}


def register(name: str) -> Callable[[PipelineFn], PipelineFn]:
    def decorator(fn: PipelineFn) -> PipelineFn:
        PIPELINE_CONFIGS[name] = fn
        return fn

    return decorator


def get_pipeline(name: str) -> PipelineFn:
    try:
        return PIPELINE_CONFIGS[name]
    except KeyError:
        available = ", ".join(sorted(PIPELINE_CONFIGS)) or "(none)"
        raise UnknownPipelineError(f"unknown pipelineConfig {name!r}; available: {available}") from None


class UnknownPipelineError(ValueError):
    """Raised when a run names a pipeline config that is not registered."""


PROMPT_VERSIONS = {
    "legacy-only": "none",
    "legacy+optimize": f"{MT_OPTIMIZE_PROMPT_VERSION}+{QPS_PROMPT_VERSION}",
    "legacy+optimize+glossary": f"{MT_OPTIMIZE_PROMPT_VERSION}+{QPS_PROMPT_VERSION}",
    "legacy+optimize+glossary+cache": f"{MT_OPTIMIZE_PROMPT_VERSION}+{QPS_PROMPT_VERSION}",
}


def prompt_version_for(pipeline_config: str) -> str:
    """Prompt versions behind a config (QPS included: the runner judges every case)."""
    return PROMPT_VERSIONS.get(pipeline_config, "none")


@register("legacy-only")
async def legacy_only(case: CaseInput, ctx: PipelineContext) -> CaseOutput:
    """Baseline: output the raw MT text with no model call.

    Eval golden cases carry no raw MT, so the harness echoes the source text
    in that case. Tokens and cost stay zero either way; nothing is a fallback.
    """
    _ = ctx
    if case.raw_mt_text:
        return CaseOutput(produced_translation=case.raw_mt_text)
    return CaseOutput(produced_translation=case.source_text)


async def _optimize_case(case: CaseInput, ctx: PipelineContext, *, use_glossary: bool, use_cache: bool) -> CaseOutput:
    raw = case.raw_mt_text or case.source_text
    terms = list(case.glossary_terms) if use_glossary else []
    pricing = ctx.pricing or Pricing()

    async def produce() -> cache.Produced:
        result = await mt_optimize.optimize(
            ctx.chat,
            source_text=case.source_text,
            raw_mt_text=raw,
            locale_code=case.locale_code,
            glossary_terms=terms,
            pricing=pricing,
        )
        return cache.Produced(
            translation=result.optimized_translation,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            cost_usd=result.cost_usd,
            fallback=result.fallback,
        )

    if use_cache:
        if ctx.conn is None or ctx.project_id is None:
            raise ValueError("cached pipeline configs need ctx.conn and ctx.project_id")
        outcome = await cache.translate_with_cache(
            ctx.conn,
            ctx.embed,
            produce,
            project_id=ctx.project_id,
            locale_code=case.locale_code,
            source_text=case.source_text,
            threshold=ctx.cache_threshold,
            expected_dimensions=ctx.embedding_dimensions,
            pricing=pricing,
        )
        return CaseOutput(
            produced_translation=outcome.translation,
            input_tokens=outcome.input_tokens,
            output_tokens=outcome.output_tokens,
            embedding_tokens=outcome.embedding_tokens,
            latency_ms=outcome.latency_ms,
            cost_usd=outcome.cost_usd,
            cache_hit=outcome.cache_hit,
            fallback=outcome.fallback,
            details=outcome.details,
        )

    produced = await produce()
    return CaseOutput(
        produced_translation=produced.translation,
        input_tokens=produced.input_tokens,
        output_tokens=produced.output_tokens,
        latency_ms=produced.latency_ms,
        cost_usd=produced.cost_usd,
        fallback=produced.fallback,
    )


@register("legacy+optimize")
async def legacy_optimize(case: CaseInput, ctx: PipelineContext) -> CaseOutput:
    """Baseline plus an ungrounded MT Optimize pass (no glossary terms)."""
    return await _optimize_case(case, ctx, use_glossary=False, use_cache=False)


@register("legacy+optimize+glossary")
async def legacy_optimize_glossary(case: CaseInput, ctx: PipelineContext) -> CaseOutput:
    """MT Optimize grounded on the locale's applicable glossary terms."""
    return await _optimize_case(case, ctx, use_glossary=True, use_cache=False)


@register("legacy+optimize+glossary+cache")
async def legacy_optimize_glossary_cache(case: CaseInput, ctx: PipelineContext) -> CaseOutput:
    """Glossary-grounded MT Optimize behind the semantic cache."""
    return await _optimize_case(case, ctx, use_glossary=True, use_cache=True)

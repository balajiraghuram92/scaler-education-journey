"""The Part F.2 pipeline endpoints: translate-and-optimize, qps-score,
comet-score, auto-route.

Shapes follow F.2, extended as the LA3 block requires: every response carries
tokens used, latency, and whether a fallback occurred. Two further additions
make the E.5 flow work end to end: translate-and-optimize returns the
deterministic check results, and auto-route accepts them (F.2 shows neither).
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.auth import require_api_key
from app.db import fetch_project
from app.evals import metrics
from app.pipeline import auto_route, cache, mt_optimize, qps
from app.pipeline.cost import Pricing

router = APIRouter(dependencies=[Depends(require_api_key)])


def _pricing(request: Request) -> Pricing:
    return Pricing.from_settings(request.app.state.settings)


class GlossaryTermInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: str = Field(min_length=1)
    target: str = Field(min_length=1)


class TranslateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    raw_mt_text: str = Field(alias="rawMtText")
    source_text: str = Field(alias="sourceText", min_length=1)
    target_locale: str = Field(alias="targetLocale", min_length=1)
    project_slug: str = Field(alias="projectSlug", min_length=1)
    glossary_terms: list[GlossaryTermInput] = Field(alias="glossaryTerms", default_factory=list)


class TranslateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    optimized_translation: str = Field(alias="optimizedTranslation")
    cache_hit: bool = Field(alias="cacheHit")
    checks: dict[str, bool]
    input_tokens: int = Field(alias="inputTokens")
    output_tokens: int = Field(alias="outputTokens")
    embedding_tokens: int = Field(alias="embeddingTokens")
    tokens_used: int = Field(alias="tokensUsed")
    latency_ms: int = Field(alias="latencyMs")
    cost_usd: float = Field(alias="costUsd")
    fallback: bool


@router.post("/translate-and-optimize", response_model=TranslateResponse)
async def translate_and_optimize(body: TranslateRequest, request: Request):
    settings = request.app.state.settings
    pricing = _pricing(request)
    terms = [(t.source, t.target) for t in body.glossary_terms]
    outcome_checks: dict[str, dict[str, bool]] = {}

    async def produce() -> cache.Produced:
        result = await mt_optimize.optimize(
            request.app.state.chat_provider,
            source_text=body.source_text,
            raw_mt_text=body.raw_mt_text,
            locale_code=body.target_locale,
            glossary_terms=terms,
            pricing=pricing,
        )
        outcome_checks["checks"] = result.checks
        return cache.Produced(
            translation=result.optimized_translation,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            cost_usd=result.cost_usd,
            fallback=result.fallback,
        )

    async with request.app.state.pool.connection() as conn:
        project = await fetch_project(conn, body.project_slug)
        if project is None:
            raise HTTPException(status_code=404, detail=f"unknown project slug {body.project_slug!r}")
        outcome = await cache.translate_with_cache(
            conn,
            request.app.state.embedding_provider,
            produce,
            project_id=project.id,
            locale_code=body.target_locale,
            source_text=body.source_text,
            threshold=settings.cache_similarity_threshold,
            expected_dimensions=settings.embedding_dimensions,
            pricing=pricing,
        )
        await conn.commit()
    # On a cache hit the producer never ran: recompute the deterministic
    # checks on the cached translation so the caller always gets them.
    checks = outcome_checks.get("checks")
    if checks is None:
        applicable = metrics.applicable_glossary_terms(body.source_text, terms)
        placeholders = metrics.placeholder_preserved_ok(body.source_text, outcome.translation)
        glossary = metrics.glossary_adherence_ok(body.source_text, outcome.translation, applicable)
        checks = {
            "placeholders_preserved": placeholders if placeholders is not None else True,
            "glossary_present": glossary if glossary is not None else True,
            "non_empty": bool(outcome.translation.strip()),
            "differs_from_source": outcome.translation.strip() != body.source_text.strip(),
        }
    return TranslateResponse(
        optimizedTranslation=outcome.translation,
        cacheHit=outcome.cache_hit,
        checks=checks,
        inputTokens=outcome.input_tokens,
        outputTokens=outcome.output_tokens,
        embeddingTokens=outcome.embedding_tokens,
        tokensUsed=outcome.input_tokens + outcome.output_tokens + outcome.embedding_tokens,
        latencyMs=outcome.latency_ms,
        costUsd=outcome.cost_usd,
        fallback=outcome.fallback,
    )


class QpsScoreRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_text: str = Field(alias="sourceText", min_length=1)
    target_text: str = Field(alias="targetText")
    target_locale: str = Field(alias="targetLocale", min_length=1)


class QpsScoreResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    score: int | None
    flagged_issues: list[str] = Field(alias="flaggedIssues")
    input_tokens: int = Field(alias="inputTokens")
    output_tokens: int = Field(alias="outputTokens")
    tokens_used: int = Field(alias="tokensUsed")
    latency_ms: int = Field(alias="latencyMs")
    cost_usd: float = Field(alias="costUsd")
    fallback: bool


@router.post("/qps-score", response_model=QpsScoreResponse)
async def qps_score(body: QpsScoreRequest, request: Request):
    result = await qps.score(
        request.app.state.chat_provider,
        source_text=body.source_text,
        target_text=body.target_text,
        locale_code=body.target_locale,
        pricing=_pricing(request),
    )
    return QpsScoreResponse(
        score=result.score,
        flaggedIssues=result.flagged_issues,
        inputTokens=result.input_tokens,
        outputTokens=result.output_tokens,
        tokensUsed=result.input_tokens + result.output_tokens,
        latencyMs=result.latency_ms,
        costUsd=result.cost_usd,
        fallback=result.fallback,
    )


class CometScoreRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_text: str = Field(alias="sourceText", min_length=1)
    target_text: str = Field(alias="targetText")
    target_locale: str = Field(alias="targetLocale", min_length=1)


class CometScoreResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    score: float | None
    available: bool
    tokens_used: int = Field(alias="tokensUsed")
    latency_ms: int = Field(alias="latencyMs")
    fallback: bool


@router.post("/comet-score", response_model=CometScoreResponse)
async def comet_score(body: CometScoreRequest, request: Request):
    _ = body.target_locale  # part of the F.2 contract; Kiwi scores (source, target) pairs
    scorer = request.app.state.comet_scorer
    start = time.perf_counter()
    scores = scorer.score_batch([body.source_text], [body.target_text]) if scorer is not None else [None]
    return CometScoreResponse(
        score=scores[0],
        available=scorer is not None and scorer.available,
        tokensUsed=0,
        latencyMs=int((time.perf_counter() - start) * 1000),
        fallback=False,
    )


class AutoRouteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    qps_score: int | None = Field(alias="qpsScore")
    project_threshold: int = Field(alias="projectThreshold")
    checks: dict[str, bool] | None = None


class AutoRouteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    needs_review: bool = Field(alias="needsReview")
    reasons: list[str]
    tokens_used: int = Field(alias="tokensUsed")
    latency_ms: int = Field(alias="latencyMs")
    fallback: bool


@router.post("/auto-route", response_model=AutoRouteResponse)
async def auto_route_endpoint(body: AutoRouteRequest):
    start = time.perf_counter()
    decision = auto_route.route(qps_score=body.qps_score, qps_threshold=body.project_threshold, checks=body.checks)
    return AutoRouteResponse(
        needsReview=decision.needs_review,
        reasons=decision.reasons,
        tokensUsed=0,
        latencyMs=int((time.perf_counter() - start) * 1000),
        fallback=False,
    )

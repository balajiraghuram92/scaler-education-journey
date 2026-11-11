"""POST /run-eval: run the golden set through a pipeline config."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.auth import require_api_key
from app.evals.runner import EmptyGoldenSetError, UnknownProjectError, run_eval
from app.pipeline.cost import Pricing
from app.pipeline.registry import PipelineContext, UnknownPipelineError

router = APIRouter(dependencies=[Depends(require_api_key)])


class RunEvalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_slug: str = Field(alias="projectSlug", min_length=1)
    pipeline_config: str = Field(alias="pipelineConfig", min_length=1)


class RunEvalResponse(BaseModel):
    """The Part F.2 run-eval response contract (camelCase), plus the LA3
    additions: tokens used, fallback count, and the prompt version behind
    the run (returned, not persisted — no EvalRun column exists yet)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    eval_run_id: int = Field(alias="evalRunId")
    avg_comet_kiwi: float | None = Field(alias="avgCometKiwi")
    avg_qps_score: float | None = Field(alias="avgQpsScore")
    glossary_adherence_rate: float | None = Field(alias="glossaryAdherenceRate")
    placeholder_preservation_rate: float | None = Field(alias="placeholderPreservationRate")
    cache_hit_rate: float | None = Field(alias="cacheHitRate")
    avg_latency_ms: int | None = Field(alias="avgLatencyMs")
    total_cost_usd: float = Field(alias="totalCostUsd")
    tokens_used: int = Field(alias="tokensUsed")
    fallback_count: int = Field(alias="fallbackCount")
    prompt_version: str = Field(alias="promptVersion")


@router.post("/run-eval", response_model=RunEvalResponse)
async def run_eval_endpoint(body: RunEvalRequest, request: Request):
    settings = request.app.state.settings
    ctx = PipelineContext(
        chat=request.app.state.chat_provider,
        embed=request.app.state.embedding_provider,
        project_slug=body.project_slug,
        cache_threshold=settings.cache_similarity_threshold,
        embedding_dimensions=settings.embedding_dimensions,
        pricing=Pricing.from_settings(settings),
    )
    try:
        async with request.app.state.pool.connection() as conn:
            summary = await run_eval(
                conn,
                project_slug=body.project_slug,
                pipeline_config=body.pipeline_config,
                ctx=ctx,
                comet=request.app.state.comet_scorer,
            )
            await conn.commit()
    except UnknownProjectError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except UnknownPipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except EmptyGoldenSetError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return RunEvalResponse(
        eval_run_id=summary.eval_run_id,
        avg_comet_kiwi=summary.avg_comet_kiwi,
        avg_qps_score=summary.avg_qps_score,
        glossary_adherence_rate=summary.glossary_adherence_rate,
        placeholder_preservation_rate=summary.placeholder_preservation_rate,
        cache_hit_rate=summary.cache_hit_rate,
        avg_latency_ms=summary.avg_latency_ms,
        total_cost_usd=summary.total_cost_usd,
        tokens_used=summary.tokens_used,
        fallback_count=summary.fallback_count,
        prompt_version=summary.prompt_version,
    )

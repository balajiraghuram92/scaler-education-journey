"""Ported from api/Services/Localization/LocalizationAiClient.cs.

Typed httpx client for the localization-ai Python service (Part F.2
endpoints). Raises NotImplementedError when no base URL is configured so the
Phase 3 actions keep surfacing HTTP 501; raises LocalizationAiException for
any operational failure (transport, timeout, non-success status, bad
payload).
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx

from ...settings import LocalizationAiSettings, get_settings

logger = logging.getLogger(__name__)

NOT_CONFIGURED_MESSAGE = (
    "The localization-ai service is not configured (LocalizationAi:BaseUrl). "
    "Configure the AI service base URL to enable MT Optimize, QPS scoring and Auto-Route."
)

T = TypeVar("T")


class LocalizationAiException(Exception):
    pass


@dataclass
class AiGlossaryTermDto:
    source: str
    target: str


@dataclass
class OptimizeTranslationResult:
    optimized_translation: str
    cache_hit: bool
    checks: dict[str, bool]
    input_tokens: int
    output_tokens: int
    tokens_used: int
    latency_ms: int
    fallback: bool


@dataclass
class AiQpsScoreResult:
    score: int | None
    flagged_issues: list[str]
    tokens_used: int
    latency_ms: int
    fallback: bool


@dataclass
class AiCometScoreResult:
    score: float | None
    available: bool
    latency_ms: int


@dataclass
class AiAutoRouteResult:
    needs_review: bool
    reasons: list[str]


@dataclass
class AiEvalRunResult:
    eval_run_id: int
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


def _insensitive(payload: dict[str, Any]) -> Callable[[str], Any]:
    """Case-insensitive key lookup, mirroring PropertyNameCaseInsensitive."""
    lowered = {str(key).lower(): value for key, value in payload.items()}

    def get(name: str) -> Any:
        return lowered.get(name.lower())

    return get


def _as_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected int, got {value!r}")
    return value


def _as_opt_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected int, got {value!r}")
    return value


def _as_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"expected number, got {value!r}")
    return float(value)


def _as_opt_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"expected number, got {value!r}")
    return float(value)


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise TypeError(f"expected string, got {value!r}")
    return value


def _as_bool(value: Any) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise TypeError(f"expected bool, got {value!r}")
    return value


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"expected list, got {value!r}")
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"expected string list item, got {item!r}")
    return list(value)


def _as_bool_map(value: Any) -> dict[str, bool]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError(f"expected object, got {value!r}")
    result: dict[str, bool] = {}
    for key, item in value.items():
        if not isinstance(item, bool):
            raise TypeError(f"expected bool map value, got {item!r}")
        result[str(key)] = item
    return result


class LocalizationAiClient:
    def __init__(
        self,
        options: LocalizationAiSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._options = options or get_settings().localization_ai
        self._http_client = http_client

    @property
    def is_configured(self) -> bool:
        return bool(self._options.base_url and self._options.base_url.strip())

    def _base_url(self) -> str:
        base_url = self._options.base_url
        if not base_url.endswith("/"):
            base_url += "/"
        return base_url

    def _timeout(self) -> float:
        return float(self._options.timeout_seconds if self._options.timeout_seconds > 0 else 60)

    async def translate_and_optimize_async(
        self,
        source_text: str,
        raw_mt_text: str,
        target_locale: str,
        project_slug: str,
        glossary_terms: list[AiGlossaryTermDto] | None,
    ) -> OptimizeTranslationResult:
        body: dict[str, Any] = {
            "rawMtText": raw_mt_text,
            "sourceText": source_text,
            "targetLocale": target_locale,
            "projectSlug": project_slug,
            "glossaryTerms": [
                {"source": term.source, "target": term.target}
                for term in (glossary_terms or [])
            ],
        }

        def build(payload: dict[str, Any]) -> OptimizeTranslationResult:
            get = _insensitive(payload)
            return OptimizeTranslationResult(
                optimized_translation=_as_str(get("optimizedTranslation")),
                cache_hit=_as_bool(get("cacheHit")),
                checks=_as_bool_map(get("checks")),
                input_tokens=_as_int(get("inputTokens")),
                output_tokens=_as_int(get("outputTokens")),
                tokens_used=_as_int(get("tokensUsed")),
                latency_ms=_as_int(get("latencyMs")),
                fallback=_as_bool(get("fallback")),
            )

        return await self._post_async("translate-and-optimize", body, build)

    async def score_qps_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> AiQpsScoreResult:
        body = {
            "sourceText": source_text,
            "targetText": target_text,
            "targetLocale": target_locale,
        }

        def build(payload: dict[str, Any]) -> AiQpsScoreResult:
            get = _insensitive(payload)
            return AiQpsScoreResult(
                score=_as_opt_int(get("score")),
                flagged_issues=_as_str_list(get("flaggedIssues")),
                tokens_used=_as_int(get("tokensUsed")),
                latency_ms=_as_int(get("latencyMs")),
                fallback=_as_bool(get("fallback")),
            )

        return await self._post_async("qps-score", body, build)

    async def score_comet_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> AiCometScoreResult:
        body = {
            "sourceText": source_text,
            "targetText": target_text,
            "targetLocale": target_locale,
        }

        def build(payload: dict[str, Any]) -> AiCometScoreResult:
            get = _insensitive(payload)
            return AiCometScoreResult(
                score=_as_opt_float(get("score")),
                available=_as_bool(get("available")),
                latency_ms=_as_int(get("latencyMs")),
            )

        return await self._post_async("comet-score", body, build)

    async def auto_route_async(
        self,
        qps_score: int | None,
        project_threshold: int,
        checks: dict[str, bool] | None,
    ) -> AiAutoRouteResult:
        body: dict[str, Any] = {
            "qpsScore": qps_score,
            "projectThreshold": project_threshold,
            "checks": checks,
        }

        def build(payload: dict[str, Any]) -> AiAutoRouteResult:
            get = _insensitive(payload)
            return AiAutoRouteResult(
                needs_review=_as_bool(get("needsReview")),
                reasons=_as_str_list(get("reasons")),
            )

        return await self._post_async("auto-route", body, build)

    async def run_eval_async(
        self, project_slug: str, pipeline_config: str
    ) -> AiEvalRunResult:
        body = {"projectSlug": project_slug, "pipelineConfig": pipeline_config}

        def build(payload: dict[str, Any]) -> AiEvalRunResult:
            get = _insensitive(payload)
            return AiEvalRunResult(
                eval_run_id=_as_int(get("evalRunId")),
                avg_comet_kiwi=_as_opt_float(get("avgCometKiwi")),
                avg_qps_score=_as_opt_float(get("avgQpsScore")),
                glossary_adherence_rate=_as_opt_float(get("glossaryAdherenceRate")),
                placeholder_preservation_rate=_as_opt_float(
                    get("placeholderPreservationRate")
                ),
                cache_hit_rate=_as_opt_float(get("cacheHitRate")),
                avg_latency_ms=_as_opt_int(get("avgLatencyMs")),
                total_cost_usd=_as_float(get("totalCostUsd")),
                tokens_used=_as_int(get("tokensUsed")),
                fallback_count=_as_int(get("fallbackCount")),
                prompt_version=_as_str(get("promptVersion")),
            )

        return await self._post_async("run-eval", body, build)

    async def _post_async(
        self, path: str, body: dict[str, Any], build: Callable[[dict[str, Any]], T]
    ) -> T:
        if not self.is_configured:
            raise NotImplementedError(NOT_CONFIGURED_MESSAGE)

        headers: dict[str, str] = {}
        if self._options.shared_secret and self._options.shared_secret.strip():
            headers["x-api-key"] = self._options.shared_secret

        client = self._http_client
        owns_client = client is None
        if client is None:
            client = httpx.AsyncClient(
                base_url=self._base_url(),
                timeout=self._timeout(),
                follow_redirects=True,
            )
        try:
            try:
                response = await client.post(path, json=body, headers=headers)
                response_json = response.text
                if response.status_code >= 400:
                    logger.error(
                        "localization-ai POST %s failed with status %s: %s",
                        path,
                        response.status_code,
                        response_json,
                    )
                    raise LocalizationAiException(
                        f"localization-ai error: {response.status_code} {response.reason_phrase}"
                    )
                try:
                    parsed = json.loads(response_json) if response_json else None
                except json.JSONDecodeError as exc:
                    logger.error(
                        "localization-ai POST %s returned an unreadable payload: %s",
                        path,
                        exc,
                    )
                    raise LocalizationAiException(
                        f"localization-ai POST {path} returned an unreadable payload."
                    ) from exc
                if parsed is None:
                    raise LocalizationAiException(
                        f"localization-ai POST {path} returned an empty payload."
                    )
                if not isinstance(parsed, dict):
                    logger.error(
                        "localization-ai POST %s returned an unreadable payload", path
                    )
                    raise LocalizationAiException(
                        f"localization-ai POST {path} returned an unreadable payload."
                    )
                try:
                    return build(parsed)
                except (TypeError, ValueError, KeyError, AttributeError) as exc:
                    logger.error(
                        "localization-ai POST %s returned an unreadable payload: %s",
                        path,
                        exc,
                    )
                    raise LocalizationAiException(
                        f"localization-ai POST {path} returned an unreadable payload."
                    ) from exc
            except LocalizationAiException:
                raise
            except Exception as exc:
                logger.error(
                    "Exception communicating with localization-ai POST %s: %s", path, exc
                )
                raise LocalizationAiException(
                    f"localization-ai POST {path} failed: {exc}"
                ) from exc
        finally:
            if owns_client:
                await client.aclose()

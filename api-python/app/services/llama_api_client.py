"""Ported from api/Services/LlamaApiClient.cs."""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

import httpx

from ..settings import LlamaApiSettings, get_environment, get_settings

logger = logging.getLogger(__name__)


@dataclass
class LlamaCompletionResult:
    reply_content: str
    prompt_tokens: int
    completion_tokens: int
    usage_estimated: bool
    estimated_cost_usd: Decimal
    latency_ms: int


@dataclass
class ChatPromptMessage:
    role: str
    content: str


class LlamaApiClient:
    def __init__(
        self,
        options: LlamaApiSettings | None = None,
        is_production: bool | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._options = options or get_settings().llama_api
        if is_production is None:
            is_production = get_environment().lower() == "production"
        self._is_production = is_production
        self._http_client = http_client

    def _base_url(self) -> str:
        base_url = (
            self._options.base_url
            if self._options.base_url and self._options.base_url.strip()
            else "https://api.llama.com/v1/"
        )
        if not base_url.endswith("/"):
            base_url += "/"
        return base_url

    def _timeout(self) -> float:
        return float(self._options.timeout_seconds if self._options.timeout_seconds > 0 else 30)

    async def generate_completion(
        self, messages: list[ChatPromptMessage]
    ) -> LlamaCompletionResult:
        started = time.perf_counter()

        api_messages = [{"role": m.role, "content": m.content} for m in messages]
        full_prompt_text = "".join(m.content + "\n" for m in messages)

        # If API key is not configured, provide a helpful mock response in development
        if not self._options.api_key or not self._options.api_key.strip():
            if self._is_production:
                raise RuntimeError("LlamaApi:ApiKey is not configured.")
            mock_reply = "Hello! The Meta Llama API key is currently not configured on this instance. Please configure `LlamaApi:ApiKey` in appsettings or `LlamaApi__ApiKey` in environment variables."
            mock_prompt_tokens, mock_comp_tokens, mock_est = _estimate_tokens(
                full_prompt_text, mock_reply
            )
            mock_cost = self._calculate_cost(mock_prompt_tokens, mock_comp_tokens)
            return LlamaCompletionResult(
                reply_content=mock_reply,
                prompt_tokens=mock_prompt_tokens,
                completion_tokens=mock_comp_tokens,
                usage_estimated=mock_est,
                estimated_cost_usd=mock_cost,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

        model = (
            self._options.model
            if self._options.model and self._options.model.strip()
            else "Llama-4-Maverick-17B-128E-Instruct-FP8"
        )
        payload = {"model": model, "messages": api_messages, "temperature": 0.7}

        client = self._http_client
        owns_client = client is None
        if client is None:
            client = httpx.AsyncClient(
                base_url=self._base_url(),
                timeout=self._timeout(),
                follow_redirects=True,
                headers={"Authorization": f"Bearer {self._options.api_key}"},
            )
        try:
            try:
                response = await client.post("chat/completions", json=payload)
                latency_ms = int((time.perf_counter() - started) * 1000)
                response_json = response.text
                if response.status_code >= 400:
                    logger.error(
                        "Llama API call failed with status %s: %s",
                        response.status_code,
                        response_json,
                    )
                    reason = response.reason_phrase
                    raise RuntimeError(f"Llama API error: {response.status_code} {reason}")

                root = json.loads(response_json)
                reply_text = ""
                choices = root.get("choices") or []
                if len(choices) > 0:
                    message = (choices[0] or {}).get("message") or {}
                    content = message.get("content")
                    reply_text = content if isinstance(content, str) else ""

                prompt_tokens, completion_tokens, usage_estimated = self._try_parse_usage(
                    root, full_prompt_text, reply_text
                )
                estimated_cost_usd = self._calculate_cost(prompt_tokens, completion_tokens)
                return LlamaCompletionResult(
                    reply_content=reply_text,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    usage_estimated=usage_estimated,
                    estimated_cost_usd=estimated_cost_usd,
                    latency_ms=latency_ms,
                )
            except RuntimeError:
                raise
            except Exception as exc:
                logger.error("Exception encountered communicating with Llama API: %s", exc)
                raise
        finally:
            if owns_client:
                await client.aclose()

    def _try_parse_usage(
        self, root: dict, prompt_text: str, reply_text: str
    ) -> tuple[int, int, bool]:
        try:
            usage = root.get("usage")
            if isinstance(usage, dict):
                prompt_value = usage.get("prompt_tokens")
                comp_value = usage.get("completion_tokens")
                has_prompt = (
                    isinstance(prompt_value, int)
                    and not isinstance(prompt_value, bool)
                    and prompt_value >= 0
                )
                has_comp = (
                    isinstance(comp_value, int)
                    and not isinstance(comp_value, bool)
                    and comp_value >= 0
                )
                if has_prompt and has_comp:
                    return (prompt_value, comp_value, False)
        except Exception as exc:
            logger.warning(
                "Failed parsing token usage from Llama API response; using character-based fallback estimation: %s",
                exc,
            )
        logger.warning(
            "Token usage missing or malformed in Llama API response. Falling back to character estimation."
        )
        return _estimate_tokens(prompt_text, reply_text)

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        total = (
            Decimal(prompt_tokens) * self._options.price_per_million_input_tokens_usd
            + Decimal(completion_tokens) * self._options.price_per_million_output_tokens_usd
        ) / Decimal(1_000_000)
        return total.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)


def _estimate_tokens(prompt_text: str, reply_text: str) -> tuple[int, int, bool]:
    # Character fallback estimation: ceil(chars / 4.0)
    prompt_tokens = math.ceil(len(prompt_text or "") / 4.0)
    completion_tokens = math.ceil(len(reply_text or "") / 4.0)
    if prompt_tokens <= 0:
        prompt_tokens = 1
    if completion_tokens <= 0:
        completion_tokens = 1
    return (prompt_tokens, completion_tokens, True)

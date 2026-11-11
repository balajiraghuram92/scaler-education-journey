"""QPS scoring stage: blind LLM-as-judge, four dimensions x 0-25.

Inputs: a chat provider, the English source text, the target translation,
and the target locale. The judge never sees which system produced the
translation. Source and target are untrusted input in delimited blocks.

Outputs: a QpsResult with the summed 0-100 score (None on fallback), flagged
issues, per-dimension justifications, token counts, latency, computed cost,
and the prompt version.

Failure behaviour: same retry rule as MT Optimize — malformed output is
retried once with the validation error, then score=None with fallback=True.
Provider exceptions fall back immediately.
"""

import time
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from app.pipeline import structured
from app.pipeline.cost import Pricing, llm_cost_usd
from app.pipeline.prompts import QPS_PROMPT_VERSION, render
from app.providers.base import ChatMessage, ChatProvider

PROMPT_VERSION = QPS_PROMPT_VERSION
TEMPLATE = "qps_judge_v1.txt"


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=25)
    justification: str = Field(min_length=1)


class JudgeOutput(BaseModel):
    accuracy: DimensionScore
    fluency: DimensionScore
    terminology: DimensionScore
    tone: DimensionScore
    flagged_issues: list[str] = []


@dataclass(frozen=True)
class QpsResult:
    score: int | None
    flagged_issues: list[str] = field(default_factory=list)
    justifications: dict[str, str] = field(default_factory=dict)
    fallback: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    prompt_version: str = PROMPT_VERSION


def _to_result(parsed: JudgeOutput, fallback: bool, input_tokens: int, output_tokens: int, latency_ms: int,
               rates: Pricing) -> QpsResult:
    return QpsResult(
        score=parsed.accuracy.score + parsed.fluency.score + parsed.terminology.score + parsed.tone.score,
        flagged_issues=list(parsed.flagged_issues),
        justifications={
            "accuracy": parsed.accuracy.justification,
            "fluency": parsed.fluency.justification,
            "terminology": parsed.terminology.justification,
            "tone": parsed.tone.justification,
        },
        fallback=fallback,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=llm_cost_usd(
            input_tokens, output_tokens, input_per_1k_usd=rates.chat_in_per_1k_usd,
            output_per_1k_usd=rates.chat_out_per_1k_usd,
        ),
    )


def _fallback_result(input_tokens: int, output_tokens: int, latency_ms: int, rates: Pricing) -> QpsResult:
    return QpsResult(
        score=None,
        fallback=True,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=llm_cost_usd(
            input_tokens, output_tokens, input_per_1k_usd=rates.chat_in_per_1k_usd,
            output_per_1k_usd=rates.chat_out_per_1k_usd,
        ),
    )


async def score(
    chat: ChatProvider,
    *,
    source_text: str,
    target_text: str,
    locale_code: str,
    pricing: Pricing | None = None,
) -> QpsResult:
    """Judge a translation blind; see module docstring."""
    rates = pricing or Pricing()
    prompt = render(TEMPLATE, locale_code=locale_code, source_text=source_text, target_text=target_text)
    messages = [ChatMessage(role="user", content=prompt)]

    start = time.perf_counter()
    try:
        first = await chat.chat(messages, json_mode=True)
    except Exception:
        return _fallback_result(0, 0, int((time.perf_counter() - start) * 1000), rates)
    try:
        parsed = structured.parse_or_raise(first.text, JudgeOutput)
    except ValueError as first_error:
        retry_messages = messages + [
            ChatMessage(role="assistant", content=first.text),
            ChatMessage(
                role="user",
                content=f"The previous response was invalid: {first_error}."
                " Reply with ONLY a single valid JSON object matching the required schema.",
            ),
        ]
        try:
            second = await chat.chat(retry_messages, json_mode=True)
        except Exception:
            return _fallback_result(
                first.input_tokens,
                first.output_tokens,
                int((time.perf_counter() - start) * 1000),
                rates,
            )
        try:
            parsed = structured.parse_or_raise(second.text, JudgeOutput)
        except ValueError:
            return _fallback_result(
                first.input_tokens + second.input_tokens,
                first.output_tokens + second.output_tokens,
                int((time.perf_counter() - start) * 1000),
                rates,
            )
        return _to_result(
            parsed,
            False,
            first.input_tokens + second.input_tokens,
            first.output_tokens + second.output_tokens,
            int((time.perf_counter() - start) * 1000),
            rates,
        )
    return _to_result(
        parsed,
        False,
        first.input_tokens,
        first.output_tokens,
        int((time.perf_counter() - start) * 1000),
        rates,
    )

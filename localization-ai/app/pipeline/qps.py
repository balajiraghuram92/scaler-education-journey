"""QPS scoring stage: blind LLM-as-judge, one overall 1-5 score.

Inputs: a chat provider, the English source text, the target translation,
and the target locale. The judge never sees which system produced the
translation. Source and target are untrusted input in delimited blocks.

Outputs: a QpsResult with the 1-5 score (None on fallback), the judge's
one-sentence reason, flagged issues, whether the placeholder veto capped
the score, token counts, latency, computed cost, the model name, and the
prompt version.

Deterministic veto: when the target does not carry exactly the source's
placeholders, the final score is capped at 2 whatever the model says. A
source with no placeholders is never vetoed.

Failure behaviour: same retry rule as MT Optimize — malformed output is
retried once with the validation error, then score=None with fallback=True.
A score that is not an integer from 1 to 5 is malformed, never clamped.
Provider exceptions fall back immediately.
"""

import time
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, StrictInt

from app.evals import metrics
from app.pipeline import structured
from app.pipeline.cost import Pricing, llm_cost_usd
from app.pipeline.prompts import QPS_PROMPT_VERSION, render
from app.providers.base import ChatMessage, ChatProvider

PROMPT_VERSION = QPS_PROMPT_VERSION
TEMPLATE = "qps_judge_v2.txt"


class JudgeOutput(BaseModel):
    score: StrictInt = Field(ge=1, le=5)
    reason: str = ""
    flagged_issues: list[str] = []


@dataclass(frozen=True)
class QpsResult:
    score: int | None
    flagged_issues: list[str] = field(default_factory=list)
    reason: str = ""
    vetoed: bool = False
    fallback: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    model: str = ""
    prompt_version: str = PROMPT_VERSION


def _to_result(
    parsed: JudgeOutput,
    fallback: bool,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    rates: Pricing,
    *,
    source_text: str,
    target_text: str,
    model: str,
) -> QpsResult:
    issues = list(parsed.flagged_issues)
    vetoed = False
    final_score: int = parsed.score
    if metrics.placeholder_preserved_ok(source_text, target_text) is False:
        vetoed = True
        final_score = min(parsed.score, 2)
        if "placeholder_mismatch" not in issues:
            issues.append("placeholder_mismatch")
    return QpsResult(
        score=final_score,
        flagged_issues=issues,
        reason=parsed.reason,
        vetoed=vetoed,
        fallback=fallback,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=llm_cost_usd(
            input_tokens, output_tokens, input_per_1k_usd=rates.chat_in_per_1k_usd,
            output_per_1k_usd=rates.chat_out_per_1k_usd,
        ),
        model=model,
    )


def _fallback_result(input_tokens: int, output_tokens: int, latency_ms: int, rates: Pricing, model: str) -> QpsResult:
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
        model=model,
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
    model = chat.name
    prompt = render(TEMPLATE, locale_code=locale_code, source_text=source_text, target_text=target_text)
    messages = [ChatMessage(role="user", content=prompt)]

    start = time.perf_counter()
    try:
        first = await chat.chat(messages, json_mode=True)
    except Exception:
        return _fallback_result(0, 0, int((time.perf_counter() - start) * 1000), rates, model)
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
                model,
            )
        try:
            parsed = structured.parse_or_raise(second.text, JudgeOutput)
        except ValueError:
            return _fallback_result(
                first.input_tokens + second.input_tokens,
                first.output_tokens + second.output_tokens,
                int((time.perf_counter() - start) * 1000),
                rates,
                model,
            )
        return _to_result(
            parsed,
            False,
            first.input_tokens + second.input_tokens,
            first.output_tokens + second.output_tokens,
            int((time.perf_counter() - start) * 1000),
            rates,
            source_text=source_text,
            target_text=target_text,
            model=model,
        )
    return _to_result(
        parsed,
        False,
        first.input_tokens,
        first.output_tokens,
        int((time.perf_counter() - start) * 1000),
        rates,
        source_text=source_text,
        target_text=target_text,
        model=model,
    )

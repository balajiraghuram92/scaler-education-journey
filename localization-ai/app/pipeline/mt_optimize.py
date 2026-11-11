"""MT Optimize stage: glossary-grounded LLM post-edit of raw MT.

Inputs: a chat provider, the English source text, the raw MT text, the
target locale, and candidate glossary terms (only terms actually occurring
in the source are sent to the model). Source and raw MT are untrusted input:
they travel in clearly delimited data blocks the model is told never to
follow as instructions.

Outputs: an OptimizeResult with the optimized translation, whether a
fallback occurred, per-check deterministic results, token counts, latency,
computed cost, and the prompt version.

Failure behaviour: malformed model output is retried once with the
validation error; a second failure (or any provider exception) falls back
to the raw MT text with fallback=True. Deterministic checks always run on
the final output.
"""

import time
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from app.evals import metrics
from app.pipeline import structured
from app.pipeline.cost import Pricing, llm_cost_usd
from app.pipeline.prompts import MT_OPTIMIZE_PROMPT_VERSION, render
from app.providers.base import ChatMessage, ChatProvider

PROMPT_VERSION = MT_OPTIMIZE_PROMPT_VERSION
TEMPLATE = "mt_optimize_v1.txt"


class OptimizeOutput(BaseModel):
    optimized_translation: str = Field(min_length=1)


@dataclass(frozen=True)
class OptimizeResult:
    optimized_translation: str
    fallback: bool
    checks: dict[str, bool] = field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    prompt_version: str = PROMPT_VERSION


def _glossary_block(terms: list[tuple[str, str]]) -> str:
    if not terms:
        return "(no glossary terms apply to this source)"
    return "\n".join(f'- "{src}" must be rendered as "{tgt}"' for src, tgt in terms)


def _checks(source_text: str, output: str, terms: list[tuple[str, str]]) -> dict[str, bool]:
    """Deterministic post-checks; vacuous checks (nothing to verify) pass."""
    placeholders = metrics.placeholder_preserved_ok(source_text, output)
    glossary = metrics.glossary_adherence_ok(source_text, output, terms)
    return {
        "placeholders_preserved": placeholders if placeholders is not None else True,
        "glossary_present": glossary if glossary is not None else True,
        "non_empty": bool(output.strip()),
        "differs_from_source": output.strip() != source_text.strip(),
    }


async def optimize(
    chat: ChatProvider,
    *,
    source_text: str,
    raw_mt_text: str,
    locale_code: str,
    glossary_terms: list[tuple[str, str]] | None = None,
    pricing: Pricing | None = None,
) -> OptimizeResult:
    """Post-edit raw MT with glossary grounding; see module docstring."""
    terms = metrics.applicable_glossary_terms(source_text, glossary_terms or [])
    rates = pricing or Pricing()
    prompt = render(
        TEMPLATE,
        locale_code=locale_code,
        glossary_block=_glossary_block(terms),
        source_text=source_text,
        raw_mt_text=raw_mt_text,
    )
    messages = [ChatMessage(role="user", content=prompt)]

    def finish(text: str, fallback: bool, input_tokens: int, output_tokens: int, latency_ms: int) -> OptimizeResult:
        return OptimizeResult(
            optimized_translation=text,
            fallback=fallback,
            checks=_checks(source_text, text, terms),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=llm_cost_usd(
                input_tokens,
                output_tokens,
                input_per_1k_usd=rates.chat_in_per_1k_usd,
                output_per_1k_usd=rates.chat_out_per_1k_usd,
            ),
        )

    start = time.perf_counter()
    try:
        first = await chat.chat(messages, json_mode=True)
    except Exception:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return finish(raw_mt_text, True, 0, 0, latency_ms)
    try:
        parsed = structured.parse_or_raise(first.text, OptimizeOutput)
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
            latency_ms = int((time.perf_counter() - start) * 1000)
            return finish(raw_mt_text, True, first.input_tokens, first.output_tokens, latency_ms)
        try:
            parsed = structured.parse_or_raise(second.text, OptimizeOutput)
        except ValueError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return finish(
                raw_mt_text,
                True,
                first.input_tokens + second.input_tokens,
                first.output_tokens + second.output_tokens,
                latency_ms,
            )
        latency_ms = int((time.perf_counter() - start) * 1000)
        return finish(
            parsed.optimized_translation,
            False,
            first.input_tokens + second.input_tokens,
            first.output_tokens + second.output_tokens,
            latency_ms,
        )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return finish(parsed.optimized_translation, False, first.input_tokens, first.output_tokens, latency_ms)

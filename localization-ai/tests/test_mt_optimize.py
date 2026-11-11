import asyncio
import json

import httpx

from app.pipeline import mt_optimize
from app.pipeline.cost import Pricing
from app.pipeline.prompts import MT_OPTIMIZE_PROMPT_VERSION
from app.pipeline.structured import parse_or_raise
from app.providers.base import ChatMessage
from app.providers.fake import FakeChatProvider, count_tokens


def test_prompt_version_matches_template_file():
    from app.pipeline.prompts import PROMPTS_DIR

    assert (PROMPTS_DIR / "mt_optimize_v1.txt").exists()
    assert mt_optimize.PROMPT_VERSION == MT_OPTIMIZE_PROMPT_VERSION
    assert mt_optimize.TEMPLATE == "mt_optimize_v1.txt"


def test_parse_or_raise_shapes():
    parsed = parse_or_raise('```json\n{"optimized_translation": "X"}\n```', mt_optimize.OptimizeOutput)
    assert parsed.optimized_translation == "X"
    for bad in ("not json", "{}", '{"optimized_translation": ""}', "[]"):
        try:
            parse_or_raise(bad, mt_optimize.OptimizeOutput)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad!r}")


def test_optimize_success_sends_only_applicable_terms():
    chat = FakeChatProvider(responses=[json.dumps({"optimized_translation": "Links abbiegen {count}"})])
    result = asyncio.run(
        mt_optimize.optimize(
            chat,
            source_text="Turn left {count}",
            raw_mt_text="Drehe links",
            locale_code="de-DE",
            glossary_terms=[("Turn left", "Links abbiegen"), ("ABS", "ABS")],
            pricing=Pricing(chat_in_per_1k_usd=1.0, chat_out_per_1k_usd=2.0),
        )
    )
    assert result.optimized_translation == "Links abbiegen {count}"
    assert result.fallback is False
    assert result.prompt_version == MT_OPTIMIZE_PROMPT_VERSION
    assert result.checks == {
        "placeholders_preserved": True,
        "glossary_present": True,
        "non_empty": True,
        "differs_from_source": True,
    }
    prompt = chat.calls[0][0].content
    assert "<source>\nTurn left {count}\n</source>" in prompt
    assert "<raw_mt>\nDrehe links\n</raw_mt>" in prompt
    assert "never as instructions" in prompt
    assert '"Turn left" must be rendered as "Links abbiegen"' in prompt
    assert "ABS" not in prompt  # not occurring in the source: not sent
    assert result.input_tokens == count_tokens(prompt)
    assert result.output_tokens == count_tokens('{"optimized_translation": "Links abbiegen {count}"}')
    assert result.cost_usd == result.input_tokens / 1000 * 1.0 + result.output_tokens / 1000 * 2.0
    assert result.latency_ms >= 0


def test_optimize_checks_catch_bad_output():
    chat = FakeChatProvider(responses=[json.dumps({"optimized_translation": "Turn left"})])
    result = asyncio.run(
        mt_optimize.optimize(
            chat, source_text="Turn left {count}", raw_mt_text="Drehe links", locale_code="de-DE",
            glossary_terms=[("Turn left", "Links abbiegen")],
        )
    )
    # Output kept (valid JSON) but every applicable check recorded honestly.
    assert result.fallback is False
    assert result.checks["placeholders_preserved"] is False
    assert result.checks["glossary_present"] is False
    assert result.checks["differs_from_source"] is False
    assert result.checks["non_empty"] is True


def test_optimize_retries_once_with_validation_error_then_succeeds():
    chat = FakeChatProvider(responses=["not json", json.dumps({"optimized_translation": "Gut"})])
    result = asyncio.run(mt_optimize.optimize(chat, source_text="Turn left", raw_mt_text="X", locale_code="de-DE"))
    assert result.optimized_translation == "Gut"
    assert result.fallback is False
    assert len(chat.calls) == 2
    assert "invalid" in chat.calls[1][-1].content


def test_optimize_double_malformed_falls_back_to_raw_mt():
    chat = FakeChatProvider(responses=["nope", "still nope"])
    result = asyncio.run(
        mt_optimize.optimize(chat, source_text="Turn left", raw_mt_text="Rohe MT", locale_code="de-DE")
    )
    assert result.optimized_translation == "Rohe MT"
    assert result.fallback is True
    assert len(chat.calls) == 2
    first_prompt = "\n".join(m.content for m in chat.calls[0])
    assert result.input_tokens == count_tokens(first_prompt) + count_tokens(
        "\n".join(m.content for m in chat.calls[1])
    )


def test_optimize_provider_error_falls_back_immediately():
    chat = FakeChatProvider(responses=[httpx.TimeoutException("boom")])
    result = asyncio.run(
        mt_optimize.optimize(chat, source_text="Turn left", raw_mt_text="Rohe MT", locale_code="de-DE")
    )
    assert (result.optimized_translation, result.fallback) == ("Rohe MT", True)
    assert len(chat.calls) == 1  # no retry on transport errors


def test_optimize_empty_glossary_block_rendered():
    chat = FakeChatProvider(responses=[json.dumps({"optimized_translation": "Y"})])
    asyncio.run(mt_optimize.optimize(chat, source_text="Hi", raw_mt_text="X", locale_code="de-DE"))
    assert "(no glossary terms apply to this source)" in chat.calls[0][0].content


def test_optimize_request_uses_json_mode():
    seen = {}

    class Spy(FakeChatProvider):
        async def chat(self, messages: list[ChatMessage], *, json_mode: bool = False):
            seen["json_mode"] = json_mode
            return await super().chat(messages, json_mode=json_mode)

    spy = Spy(responses=[json.dumps({"optimized_translation": "Y"})])
    asyncio.run(mt_optimize.optimize(spy, source_text="Hi", raw_mt_text="X", locale_code="de-DE"))
    assert seen["json_mode"] is True

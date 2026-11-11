import asyncio
import json

import httpx

from app.pipeline import qps
from app.pipeline.cost import Pricing
from app.pipeline.prompts import QPS_PROMPT_VERSION
from app.providers.fake import FakeChatProvider, count_tokens

GOOD_JUDGEMENT = {
    "accuracy": {"score": 20, "justification": "meaning preserved"},
    "fluency": {"score": 22, "justification": "natural German"},
    "terminology": {"score": 25, "justification": "HUD kept"},
    "tone": {"score": 23, "justification": "concise HUD style"},
    "flagged_issues": ["minor word order"],
}


def test_prompt_version_matches_template_file():
    from app.pipeline.prompts import PROMPTS_DIR

    assert (PROMPTS_DIR / "qps_judge_v1.txt").exists()
    assert qps.PROMPT_VERSION == QPS_PROMPT_VERSION


def test_score_sums_dimensions_and_stays_blind():
    chat = FakeChatProvider(responses=[json.dumps(GOOD_JUDGEMENT)])
    result = asyncio.run(
        qps.score(
            chat,
            source_text="Turn left",
            target_text="Links abbiegen",
            locale_code="de-DE",
            pricing=Pricing(chat_in_per_1k_usd=1.0, chat_out_per_1k_usd=1.0),
        )
    )
    assert result.score == 90
    assert result.flagged_issues == ["minor word order"]
    assert result.justifications["accuracy"] == "meaning preserved"
    assert result.fallback is False
    assert result.prompt_version == QPS_PROMPT_VERSION
    prompt = chat.calls[0][0].content
    assert "do not know which system produced it" in prompt
    assert "<target>\nLinks abbiegen\n</target>" in prompt
    assert result.input_tokens == count_tokens(prompt)
    assert result.cost_usd == (result.input_tokens + result.output_tokens) / 1000


def test_score_retries_once_then_succeeds():
    chat = FakeChatProvider(responses=["garbage", json.dumps(GOOD_JUDGEMENT)])
    result = asyncio.run(qps.score(chat, source_text="A", target_text="B", locale_code="de-DE"))
    assert result.score == 90
    assert result.fallback is False
    assert len(chat.calls) == 2


def test_score_out_of_range_triggers_retry_then_fallback():
    bad = dict(GOOD_JUDGEMENT)
    bad["accuracy"] = {"score": 26, "justification": "too high"}
    chat = FakeChatProvider(responses=[json.dumps(bad), json.dumps(bad)])
    result = asyncio.run(qps.score(chat, source_text="A", target_text="B", locale_code="de-DE"))
    assert result.score is None
    assert result.fallback is True
    assert len(chat.calls) == 2


def test_score_double_malformed_gives_null_score():
    chat = FakeChatProvider(responses=["nope", "still nope"])
    result = asyncio.run(qps.score(chat, source_text="A", target_text="B", locale_code="de-DE"))
    assert result.score is None
    assert result.fallback is True
    assert result.flagged_issues == []


def test_score_provider_error_falls_back_immediately():
    chat = FakeChatProvider(responses=[httpx.TimeoutException("boom")])
    result = asyncio.run(qps.score(chat, source_text="A", target_text="B", locale_code="de-DE"))
    assert (result.score, result.fallback) == (None, True)
    assert len(chat.calls) == 1

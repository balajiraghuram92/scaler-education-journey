"""QPS judge calibration: hand-written good/bad translations with expected score
bands. Skipped by default; run against a real model with::

    LOCAI_REAL_CHAT=1 LOCAI_REAL_CHAT_BASE_URL=http://<vllm>:8000/v1 \\
        LOCAI_REAL_CHAT_MODEL=<name> pytest tests/test_qps_calibration.py
"""

import asyncio
import os

import pytest

from app.pipeline import qps
from app.providers.openai_compat import OpenAICompatChatProvider

REAL_CHAT = os.environ.get("LOCAI_REAL_CHAT") == "1"

# (source, target, locale, low, high, note) on the 1-5 judge scale.
CALIBRATION_CASES = [
    (
        "Turn left ahead",
        "Voraus links abbiegen",
        "de-DE",
        4,
        5,
        "good: accurate, fluent, correct term",
    ),
    (
        "Low fuel warning",
        "Kraftstoffwarnung",
        "de-DE",
        4,
        5,
        "good: approved single-noun warning form",
    ),
    (
        "HUD brightness {count}",
        "HUD-Helligkeit {count}",
        "de-DE",
        4,
        5,
        "good: acronym kept, placeholder preserved",
    ),
    (
        "Turn left ahead",
        "Turn left ahead",
        "de-DE",
        1,
        2,
        "bad: untranslated source echo",
    ),
    (
        "Low fuel warning",
        "Hoher Kraftstoffstand, alles in Ordnung",
        "de-DE",
        1,
        2,
        "bad: inverted meaning (says fuel is fine)",
    ),
    (
        "Speed limit {speed} ahead",
        "Limitation de vitesse devant",
        "fr-FR",
        1,
        2,
        "bad: dropped the {speed} placeholder (veto caps this at 2)",
    ),
]


@pytest.mark.skipif(not REAL_CHAT, reason="needs a real chat model (LOCAI_REAL_CHAT=1)")
@pytest.mark.parametrize(("source", "target", "locale", "low", "high", "note"), CALIBRATION_CASES)
def test_judge_calibration_bands(source, target, locale, low, high, note):
    async def go():
        provider = OpenAICompatChatProvider(
            base_url=os.environ.get("LOCAI_REAL_CHAT_BASE_URL", "http://localhost:8001/v1"),
            api_key=os.environ.get("LOCAI_REAL_CHAT_API_KEY", ""),
            model=os.environ["LOCAI_REAL_CHAT_MODEL"],
            timeout_seconds=120.0,
        )
        try:
            return await qps.score(provider, source_text=source, target_text=target, locale_code=locale)
        finally:
            await provider.close()

    result = asyncio.run(go())
    assert result.fallback is False, f"judge fell back on calibration case: {note}"
    assert result.score is not None
    assert low <= result.score <= high, f"score {result.score} outside [{low}, {high}]: {note}"

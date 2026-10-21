import asyncio

import pytest
from pydantic import BaseModel, ConfigDict, Field

from resilient_gen import (
    Completion,
    GenStats,
    StructuredOutputError,
    TruncatedOutput,
    extract_json,
    generate_validated,
)


class Triage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: str
    confidence: float = Field(ge=0, le=1)


GOOD = '{"category": "bug", "confidence": 0.7}'


class Script:
    """Scripted completer that records what it was asked."""

    def __init__(self, *replies: Completion) -> None:
        self._replies = list(replies)
        self.calls: list[tuple[int, int]] = []     # (message_count, max_tokens)

    async def __call__(self, messages, max_tokens):
        self.calls.append((len(messages), max_tokens))
        return self._replies.pop(0)


def run(coro):
    return asyncio.run(coro)


def msgs():
    return [{"role": "user", "content": "triage"}]


def test_extract_json_handles_strings_escapes_and_fences():
    assert extract_json('x {"a": "}{", "b": {"c": 1}} y {"z": 2}') == '{"a": "}{", "b": {"c": 1}}'
    assert extract_json('```json\n{"k": "v \\" }"}\n``` bye') == '{"k": "v \\" }"}'
    with pytest.raises(ValueError):
        extract_json('{"a": 1')
    with pytest.raises(ValueError):
        extract_json("no braces here")


def test_happy_path_makes_one_call():
    complete = Script(Completion(GOOD, "stop"))
    stats = GenStats()
    out = run(generate_validated(complete, msgs(), Triage, stats=stats))
    assert out.category == "bug"
    assert (stats.attempts, stats.repairs, stats.truncations) == (1, 0, 0)


def test_truncation_grows_the_cap_without_adding_repair_messages():
    complete = Script(Completion('{"category": "bu', "length"),
                      Completion('{"category": "bug", "conf', "length"),
                      Completion(GOOD, "stop"))
    stats = GenStats()
    run(generate_validated(complete, msgs(), Triage, max_tokens=100, max_tokens_cap=1000, stats=stats))
    assert complete.calls == [(1, 100), (1, 200), (1, 400)]
    assert (stats.attempts, stats.repairs, stats.truncations) == (3, 0, 2)


def test_truncation_at_the_cap_raises_truncated_output():
    complete = Script(Completion("{", "length"), Completion("{", "length"))
    with pytest.raises(TruncatedOutput):
        run(generate_validated(complete, msgs(), Triage, max_tokens=300, max_tokens_cap=400))
    assert [c[1] for c in complete.calls] == [300, 400]


def test_invalid_output_is_repaired_with_the_error_text():
    seen = []

    async def complete(messages, max_tokens):
        seen.append([m["content"] for m in messages])
        if len(seen) == 1:
            return Completion('{"category": "bug", "confidence": 3}', "stop")
        return Completion(GOOD, "stop")

    stats = GenStats()
    out = run(generate_validated(complete, msgs(), Triage, stats=stats))
    assert out.confidence == 0.7 and stats.repairs == 1
    repair_prompt = seen[1][-1]
    assert "confidence" in repair_prompt and "less than or equal to 1" in repair_prompt
    assert seen[1][-2].startswith('{"category"')


def test_repair_budget_is_enforced():
    bad = Completion('{"category": "bug", "confidence": 3}', "stop")
    complete = Script(bad, bad, bad, bad)
    with pytest.raises(StructuredOutputError, match="invalid after 2 repairs"):
        run(generate_validated(complete, msgs(), Triage, max_repairs=2))
    assert len(complete.calls) == 3


def test_content_filter_is_not_repaired():
    complete = Script(Completion("", "content_filter"))
    with pytest.raises(StructuredOutputError, match="content_filter"):
        run(generate_validated(complete, msgs(), Triage))
    assert len(complete.calls) == 1


def test_echoed_output_and_error_text_are_bounded():
    huge = '{"category": "' + "x" * 5000 + '", "confidence": 9}'
    seen = []

    async def complete(messages, max_tokens):
        seen.append(messages)
        return Completion(huge if len(seen) == 1 else GOOD, "stop")

    run(generate_validated(complete, msgs(), Triage))
    assert len(seen[1][-2]["content"]) <= 2000
    assert len(seen[1][-1]["content"]) < 700


def test_caller_messages_are_not_mutated():
    bad = Completion('{"category": "bug", "confidence": 3}', "stop")
    complete = Script(bad, Completion(GOOD, "stop"))
    original = msgs()
    run(generate_validated(complete, original, Triage))
    assert original == msgs(), "repair messages must be appended to a copy"
    assert complete.calls == [(1, 256), (3, 256)]


def test_truncation_and_repair_budgets_are_independent():
    complete = Script(
        Completion('{"category"', "length"),
        Completion('{"category": "bug", "confidence": 3}', "stop"),
        Completion(GOOD, "stop"),
    )
    stats = GenStats()
    out = run(generate_validated(complete, msgs(), Triage, max_repairs=1, stats=stats))
    assert out.category == "bug"
    assert (stats.attempts, stats.repairs, stats.truncations) == (3, 1, 1)
    assert complete.calls == [(1, 256), (1, 512), (3, 512)], "the grown cap is kept for the repair attempt"

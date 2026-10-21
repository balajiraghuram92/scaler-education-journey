from dataclasses import FrozenInstanceError

import pytest

from chatreq import ChatRequest, estimate_tokens


def base():
    return ChatRequest.builder().model("small-1").system("Be terse.").user("Hi")


def test_estimate_tokens():
    assert estimate_tokens("") == 1, "at least one token"
    assert estimate_tokens("abc") == 1
    assert estimate_tokens("x" * 40) == 10


def test_happy_path_defaults_and_payload():
    request = base().build()
    assert isinstance(request, ChatRequest)
    assert request.messages == (("system", "Be terse."), ("user", "Hi"))
    assert (request.temperature, request.max_tokens) == (0.2, 512), "defaults are 0.2 and 512"
    payload = request.to_payload()
    assert payload["model"] == "small-1" and payload["max_tokens"] == 512
    assert payload["messages"][1] == {"role": "user", "content": "Hi"}


def test_payload_is_a_fresh_copy():
    request = base().build()
    payload = request.to_payload()
    payload["messages"].clear()
    assert len(request.to_payload()["messages"]) == 2, "to_payload must return a fresh dict each time"


def test_required_fields():
    with pytest.raises(ValueError, match="model"):
        ChatRequest.builder().user("Hi").build()
    with pytest.raises(ValueError, match="user message"):
        ChatRequest.builder().model("m").system("x").build()


def test_system_message_rules():
    with pytest.raises(ValueError, match="first"):
        ChatRequest.builder().model("m").user("Hi").system("late").build()
    with pytest.raises(ValueError, match="only one"):
        ChatRequest.builder().model("m").system("a").system("b").user("Hi").build()


def test_temperature_and_max_tokens_ranges():
    with pytest.raises(ValueError, match="temperature"):
        base().temperature(3.0).build()
    with pytest.raises(ValueError):
        base().temperature(-0.1).build()
    assert base().temperature(2.0).build().temperature == 2.0
    assert base().temperature(0).build().temperature == 0
    with pytest.raises(ValueError):
        base().max_tokens(0).build()


def test_budget_is_checked_after_all_values_are_known():
    long_text = "x" * 4000  # about 1000 tokens
    builder = ChatRequest.builder(context_window=1200).model("m").max_tokens(500)
    builder.user(long_text)  # max_tokens was set BEFORE the long message was added
    with pytest.raises(ValueError, match="context window"):
        builder.build()
    assert builder.max_tokens(100).build().max_tokens == 100, "lowering max_tokens makes it fit"


def test_two_builds_are_independent_and_immutable():
    builder = base()
    first = builder.build()
    builder.user("second turn")
    second = builder.build()
    assert len(first.messages) == 2 and len(second.messages) == 3
    assert isinstance(first.messages, tuple)
    with pytest.raises(FrozenInstanceError):
        first.model = "other"


def test_to_builder_copies_and_changes_one_field():
    original = base().max_tokens(64).build()
    retry = original.to_builder().max_tokens(128).build()
    assert (original.max_tokens, retry.max_tokens) == (64, 128)
    assert retry.messages == original.messages and retry.model == original.model
    retry_builder = original.to_builder().user("again")
    assert len(original.messages) == 2, "changing the new builder must not touch the original request"
    assert len(retry_builder.build().messages) == 3

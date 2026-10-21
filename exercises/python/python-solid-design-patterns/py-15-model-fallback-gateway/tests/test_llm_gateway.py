import dataclasses
import types

import pytest

from llm_gateway import (
    AcmeAdapter,
    ChatReply,
    ChatRequest,
    FallbackChatModel,
    ModelUnavailable,
    NimbusAdapter,
)
from vendors import AcmeClient, NimbusClient


class SpyAcme(AcmeClient):
    def __init__(self, error=None):
        self.error, self.calls = error, []

    def create_completion(self, *, messages, max_tokens):
        self.calls.append((messages, max_tokens))
        if self.error:
            raise self.error
        return {
            "choices": [{"message": {"content": "acme says hi"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 4},
        }


class SpyNimbus(NimbusClient):
    def __init__(self, error=None):
        self.error, self.calls = error, []

    def generate(self, text, max_output_tokens):
        self.calls.append((text, max_output_tokens))
        if self.error:
            raise self.error
        return types.SimpleNamespace(output=f"n:{text}", tokens_in=3, tokens_out=2)


class FakeModel:
    def __init__(self, name, error=None):
        self.name, self.error, self.calls = name, error, 0

    def generate(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return ChatReply(f"{self.name}:{request.prompt}", 1, 1, self.name)


def test_request_and_reply_are_frozen_slotted_dataclasses():
    req = ChatRequest("hi")
    assert req.max_tokens == 256, "max_tokens defaults to 256"
    assert dataclasses.is_dataclass(ChatReply) and dataclasses.is_dataclass(ChatRequest)
    with pytest.raises(dataclasses.FrozenInstanceError):
        req.prompt = "changed"
    assert not hasattr(req, "__dict__"), "use slots=True"
    reply = ChatReply("t", 1, 2, "p")
    assert (reply.text, reply.input_tokens, reply.output_tokens, reply.provider) == ("t", 1, 2, "p")
    with pytest.raises(dataclasses.FrozenInstanceError):
        reply.text = "x"


def test_acme_adapter_normalises_request_and_reply():
    spy = SpyAcme()
    reply = AcmeAdapter(spy).generate(ChatRequest("hello", max_tokens=33))
    assert spy.calls == [([{"role": "user", "content": "hello"}], 33)], f"unexpected vendor call {spy.calls}"
    assert reply == ChatReply("acme says hi", 7, 4, "acme")


def test_nimbus_adapter_normalises_request_and_reply():
    spy = SpyNimbus()
    reply = NimbusAdapter(spy).generate(ChatRequest("hello", max_tokens=12))
    assert spy.calls == [("hello", 12)], f"unexpected vendor call {spy.calls}"
    assert reply == ChatReply("n:hello", 3, 2, "nimbus")


@pytest.mark.parametrize("error", [ConnectionError("down"), TimeoutError("slow")])
def test_adapters_translate_transport_errors_and_keep_the_cause(error):
    for adapter in (AcmeAdapter(SpyAcme(error)), NimbusAdapter(SpyNimbus(error))):
        with pytest.raises(ModelUnavailable) as info:
            adapter.generate(ChatRequest("x"))
        assert info.value.__cause__ is error, "chain the original error with 'raise ... from'"


def test_adapters_do_not_swallow_programming_errors():
    with pytest.raises(KeyError):
        AcmeAdapter(SpyAcme(KeyError("bug"))).generate(ChatRequest("x"))
    with pytest.raises(ValueError):
        NimbusAdapter(SpyNimbus(ValueError("bug"))).generate(ChatRequest("x"))


def test_fallback_uses_the_second_provider_when_the_first_is_down():
    model = FallbackChatModel([
        AcmeAdapter(SpyAcme(ConnectionError("boom"))),
        NimbusAdapter(SpyNimbus()),
    ])
    r = model.generate(ChatRequest("hi"))
    assert (r.text, r.provider, r.input_tokens, r.output_tokens) == ("n:hi", "nimbus", 3, 2)


def test_fallback_returns_first_success_without_calling_later_models():
    first, second = FakeModel("a"), FakeModel("b")
    reply = FallbackChatModel([first, second]).generate(ChatRequest("q"))
    assert reply.provider == "a"
    assert (first.calls, second.calls) == (1, 0), "later models must not be called after a success"


def test_all_failing_raises_unavailable_chained_to_the_last_failure():
    e1, e2 = ModelUnavailable("one"), ModelUnavailable("two")
    model = FallbackChatModel([FakeModel("a", e1), FakeModel("b", e2)])
    with pytest.raises(ModelUnavailable, match="all providers failed") as info:
        model.generate(ChatRequest("hi"))
    assert info.value.__cause__ is e2, "the last failure must be the __cause__"


def test_non_transport_error_propagates_and_stops_the_chain():
    boom, later = FakeModel("a", KeyError("bug")), FakeModel("b")
    with pytest.raises(KeyError):
        FallbackChatModel([boom, later]).generate(ChatRequest("hi"))
    assert later.calls == 0, "a programming error must not trigger fallback"


def test_empty_sequence_is_rejected_and_fallback_is_itself_a_chat_model():
    with pytest.raises(ValueError):
        FallbackChatModel([])
    inner = FallbackChatModel([FakeModel("x", ModelUnavailable("down"))])
    outer = FallbackChatModel([inner, FakeModel("y")])
    assert outer.generate(ChatRequest("z")).provider == "y", "FallbackChatModel must be composable like any ChatModel"

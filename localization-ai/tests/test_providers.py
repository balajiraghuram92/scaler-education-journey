import asyncio
import json
import math

import httpx
import pytest

from app.providers.base import ChatMessage
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider, count_tokens
from app.providers.openai_compat import OpenAICompatChatProvider, OpenAICompatEmbeddingProvider


def test_fake_token_count_is_documented_stand_in():
    assert count_tokens("") == 1
    assert count_tokens("abcd") == 1
    assert count_tokens("abcdefgh") == 2


def test_fake_chat_default_response_and_call_recording():
    fake = FakeChatProvider()
    result = asyncio.run(fake.chat([ChatMessage(role="user", content="hi")]))
    assert result.text == "{}"
    assert result.input_tokens == count_tokens("hi")
    assert result.output_tokens == count_tokens("{}")
    assert result.latency_ms == 1
    assert len(fake.calls) == 1
    assert fake.calls[0][0].content == "hi"


def test_fake_chat_scripted_responses_in_order():
    fake = FakeChatProvider(responses=['{"a": 1}', "not json"])
    first = asyncio.run(fake.chat([ChatMessage(role="user", content="one")]))
    second = asyncio.run(fake.chat([ChatMessage(role="user", content="two")]))
    assert first.text == '{"a": 1}'
    assert second.text == "not json"
    # Queue exhausted: back to the default.
    third = asyncio.run(fake.chat([ChatMessage(role="user", content="three")]))
    assert third.text == "{}"


def test_fake_chat_queue_and_raises_scripted_errors():
    fake = FakeChatProvider()
    fake.queue('{"ok": true}', httpx.TimeoutException("boom"))
    assert asyncio.run(fake.chat([ChatMessage(role="user", content="x")])).text == '{"ok": true}'
    with pytest.raises(httpx.TimeoutException):
        asyncio.run(fake.chat([ChatMessage(role="user", content="x")]))


def test_fake_embedding_is_deterministic_and_normalized():
    fake = FakeEmbeddingProvider(dimensions=16)
    first, second = asyncio.run(fake.embed(["Turn left", "Turn left"]))
    assert first.vector == second.vector
    assert len(first.vector) == 16
    assert math.isclose(sum(v * v for v in first.vector), 1.0, rel_tol=1e-9)
    assert first.tokens == count_tokens("Turn left")
    assert fake.calls == ["Turn left", "Turn left"]


def test_fake_embedding_differs_per_text():
    fake = FakeEmbeddingProvider(dimensions=32)
    left, right = asyncio.run(fake.embed(["Turn left", "Turn right"]))
    assert left.vector != right.vector


def test_openai_compat_chat_posts_expected_shape_and_parses_usage():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = request.read().decode()
        body = json.loads(seen["body"])
        assert body["model"] == "test-model"
        assert body["messages"] == [{"role": "user", "content": "hi"}]
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"score": 5}'}}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 3},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatChatProvider(
        base_url="http://models.test/v1", api_key="secret", model="test-model", client=client
    )
    result = asyncio.run(provider.chat([ChatMessage(role="user", content="hi")], json_mode=True))
    assert seen["url"] == "http://models.test/v1/chat/completions"
    assert seen["auth"] == "Bearer secret"
    assert result.text == '{"score": 5}'
    assert (result.input_tokens, result.output_tokens) == (7, 3)
    assert result.latency_ms >= 0


def test_openai_compat_chat_no_auth_header_without_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatChatProvider(base_url="http://x/v1", api_key="", model="m", client=client)
    result = asyncio.run(provider.chat([ChatMessage(role="user", content="hi")]))
    assert seen["auth"] is None
    assert result.text == "ok"
    assert (result.input_tokens, result.output_tokens) == (0, 0)


def test_openai_compat_embedding_splits_batch_tokens():
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "http://models.test/v1/embeddings"
        return httpx.Response(
            200,
            json={
                "data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}],
                "usage": {"prompt_tokens": 7},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatEmbeddingProvider(
        base_url="http://models.test/v1", api_key="", model="emb", dimensions=2, client=client
    )
    results = asyncio.run(provider.embed(["a", "b"]))
    assert [r.vector for r in results] == [[0.1, 0.2], [0.3, 0.4]]
    # 7 tokens over 2 texts: 4 + 3, still summing to 7.
    assert [r.tokens for r in results] == [4, 3]
    assert provider.dimensions == 2

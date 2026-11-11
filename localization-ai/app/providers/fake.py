"""Deterministic fake providers.

Every test runs on these, and the service can run with them (no model at
all) via CHAT_PROVIDER=fake / EMBEDDING_PROVIDER=fake. Token counts are a
documented stand-in (max(1, len//4)), never real tokenizer output.
"""

import hashlib
import math
import random
from collections import deque

from app.providers.base import ChatMessage, ChatResult, EmbeddingResult


def count_tokens(text: str) -> int:
    """Deterministic stand-in token count for the fake providers only."""
    return max(1, len(text) // 4)


class FakeChatProvider:
    """Scriptable fake chat provider.

    Each queued item is the next response (a string, returned verbatim) or
    the next failure (an Exception, raised). With an empty queue the default
    response is returned. Every call is recorded in ``calls``.
    """

    def __init__(self, responses: list[str | Exception] | None = None, *, default_response: str = "{}") -> None:
        self.name = "fake-chat"
        self._responses: deque[str | Exception] = deque(responses or [])
        self._default_response = default_response
        self.calls: list[list[ChatMessage]] = []

    def queue(self, *responses: str | Exception) -> None:
        self._responses.extend(responses)

    async def chat(self, messages: list[ChatMessage], *, json_mode: bool = False) -> ChatResult:
        self.calls.append(list(messages))
        item = self._responses.popleft() if self._responses else self._default_response
        if isinstance(item, Exception):
            raise item
        prompt = "\n".join(m.content for m in messages)
        return ChatResult(
            text=item,
            input_tokens=count_tokens(prompt),
            output_tokens=count_tokens(item),
            latency_ms=1,
        )

    async def close(self) -> None:
        pass


class FakeEmbeddingProvider:
    """Deterministic unit vectors from sha256(text): same text always gives
    the same vector, different texts give near-orthogonal ones."""

    def __init__(self, dimensions: int = 384) -> None:
        self.name = "fake-embed"
        self.dimensions = dimensions
        self.calls: list[str] = []

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        results = []
        for text in texts:
            self.calls.append(text)
            seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
            rng = random.Random(seed)
            vector = [rng.gauss(0, 1) for _ in range(self.dimensions)]
            norm = math.sqrt(sum(v * v for v in vector)) or 1.0
            vector = [v / norm for v in vector]
            results.append(EmbeddingResult(vector=vector, tokens=count_tokens(text), latency_ms=1))
        return results

    async def close(self) -> None:
        pass

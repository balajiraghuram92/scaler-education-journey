"""Model adapters: an OpenAI-compatible HTTP adapter and a scriptable fake."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Protocol

import httpx

# USD per 1k tokens (input, output) for the fictional Tessera model family.
PRICES: dict[str, tuple[float, float]] = {
    "tessera-small": (0.0005, 0.0015),
    "tessera-large": (0.003, 0.012),
    "tessera-embed": (0.0001, 0.0),
}


def price_of(
    model: str,
    tokens_in: int,
    tokens_out: int,
    overrides: dict[str, tuple[float, float]] | None = None,
) -> float:
    if overrides and model in overrides:
        rate_in, rate_out = overrides[model]
    else:
        rate_in, rate_out = PRICES.get(model, (0.001, 0.003))
    return (tokens_in * rate_in + tokens_out * rate_out) / 1000.0


def fake_embedding(text: str, dim: int) -> list[float]:
    """Deterministic pseudo-embedding: sha256 stream mapped to [-1, 1]."""
    out: list[float] = []
    counter = 0
    while len(out) < dim:
        digest = hashlib.sha256(f"{text}:{counter}".encode()).digest()
        out.extend((b / 127.5) - 1.0 for b in digest)
        counter += 1
    return out[:dim]


@dataclass
class AdapterResult:
    text: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class ModelAdapter(Protocol):
    async def complete(self, model: str, system: str, user: str) -> AdapterResult: ...
    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]: ...


class OpenAICompatAdapter:
    """Chat + embeddings against any OpenAI-compatible base URL."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_s: float = 120.0,
        key_header: str = "bearer",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._key_header = key_header
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        if self._key_header == "api-key":
            return {"api-key": self._api_key}
        return {"Authorization": f"Bearer {self._api_key}"}

    async def complete(self, model: str, system: str, user: str) -> AdapterResult:
        started = time.perf_counter()
        async with httpx.AsyncClient(
            timeout=self._timeout_s, transport=self._transport
        ) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
        return AdapterResult(
            text=text,
            model=model,
            tokens_in=int(usage.get("prompt_tokens", 0)),
            tokens_out=int(usage.get("completion_tokens", 0)),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]:
        async with httpx.AsyncClient(
            timeout=self._timeout_s, transport=self._transport
        ) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                headers=self._headers(),
                json={"model": model, "input": texts},
            )
            response.raise_for_status()
            payload = response.json()
        return [[float(v) for v in row["embedding"][:dim]] for row in payload["data"]]


class AnthropicMessagesAdapter:
    """Chat against Claude in Microsoft Foundry (Anthropic Messages API shape)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        version: str,
        max_tokens: int,
        timeout_s: float = 120.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._version = version
        self._max_tokens = max_tokens
        self._timeout_s = timeout_s
        self._transport = transport

    async def complete(self, model: str, system: str, user: str) -> AdapterResult:
        started = time.perf_counter()
        async with httpx.AsyncClient(
            timeout=self._timeout_s, transport=self._transport
        ) as client:
            response = await client.post(
                f"{self._base_url}/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": self._version,
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": self._max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = "".join(
            block["text"]
            for block in payload.get("content", [])
            if block.get("type") == "text"
        )
        usage = payload.get("usage", {})
        return AdapterResult(
            text=text,
            model=model,
            tokens_in=int(usage.get("input_tokens", 0)),
            tokens_out=int(usage.get("output_tokens", 0)),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]:
        raise NotImplementedError(
            "Claude has no embeddings endpoint; "
            "route the embed task to an OpenAI-compatible model"
        )


class RoutedAdapter:
    """Dispatches to the first adapter whose prefix matches the model name."""

    def __init__(
        self, default: ModelAdapter, by_prefix: list[tuple[str, ModelAdapter]]
    ) -> None:
        self._default = default
        self._by_prefix = by_prefix

    def _select(self, model: str) -> ModelAdapter:
        for prefix, adapter in self._by_prefix:
            if model.startswith(prefix):
                return adapter
        return self._default

    async def complete(self, model: str, system: str, user: str) -> AdapterResult:
        return await self._select(model).complete(model, system, user)

    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]:
        return await self._select(model).embed(model, texts, dim)


@dataclass
class FakeAdapter:
    """Deterministic, scriptable fake used by every test.

    `script` maps task type -> queue of response texts; each call pops the head.
    When a queue is empty (or the task has no entry), `default` is returned.
    """

    script: dict[str, list[str]] = field(default_factory=dict)
    defaults: dict[str, str] = field(default_factory=dict)
    default: str = "{}"
    dim: int = 64
    calls: list[tuple[str, str]] = field(default_factory=list)

    async def complete(self, model: str, system: str, user: str) -> AdapterResult:
        self.calls.append((model, user))
        queue = self.script.setdefault(model, [])
        if queue:
            text = queue.pop(0)
        else:
            text = self.default
            for prefix, canned in self.defaults.items():
                if system.startswith(prefix):
                    text = canned
                    break
        tokens_in = max(1, len(user.split()))
        tokens_out = max(1, len(text.split()))
        return AdapterResult(
            text=text, model=model, tokens_in=tokens_in, tokens_out=tokens_out, latency_ms=0
        )

    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]:
        del model
        return [fake_embedding(t, dim) for t in texts]

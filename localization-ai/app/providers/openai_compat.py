"""OpenAI-compatible HTTP providers.

Speaks ``POST {base_url}/chat/completions`` and ``POST {base_url}/embeddings``
against a self-hosted vLLM server or any compatible endpoint. Base URL, API
key and model names all come from settings; nothing is hard-coded here.
"""

import time

import httpx

from app.providers.base import ChatMessage, ChatResult, EmbeddingResult


class OpenAICompatChatProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.name = f"openai-compat:{model}"
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            return {}
        return {"Authorization": f"Bearer {self._api_key}"}

    async def chat(self, messages: list[ChatMessage], *, json_mode: bool = False) -> ChatResult:
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        start = time.perf_counter()
        response = await self._client.post(f"{self._base_url}/chat/completions", json=payload, headers=self._headers())
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"] or ""
        usage = data.get("usage") or {}
        return ChatResult(
            text=text,
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()


class OpenAICompatEmbeddingProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        dimensions: int,
        timeout_seconds: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.name = f"openai-compat:{model}"
        self.dimensions = dimensions
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            return {}
        return {"Authorization": f"Bearer {self._api_key}"}

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        start = time.perf_counter()
        response = await self._client.post(
            f"{self._base_url}/embeddings",
            json={"model": self._model, "input": texts},
            headers=self._headers(),
        )
        response.raise_for_status()
        data = response.json()
        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = data.get("usage") or {}
        # The batch reports one token total; split it evenly so per-case cost
        # sums stay exact.
        total = int(usage.get("prompt_tokens", 0))
        base, remainder = divmod(total, max(len(texts), 1))
        results = []
        for i, item in enumerate(data["data"]):
            results.append(
                EmbeddingResult(
                    vector=[float(v) for v in item["embedding"]],
                    tokens=base + (1 if i < remainder else 0),
                    latency_ms=latency_ms,
                )
            )
        return results

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

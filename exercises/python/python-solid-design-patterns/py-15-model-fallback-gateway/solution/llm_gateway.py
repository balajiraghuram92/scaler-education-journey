from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from vendors import AcmeClient, NimbusClient


class ModelUnavailable(Exception):
    """Provider-neutral failure: the model could not be reached or refused."""


@dataclass(frozen=True, slots=True)
class ChatRequest:
    prompt: str
    max_tokens: int = 256


@dataclass(frozen=True, slots=True)
class ChatReply:
    text: str
    input_tokens: int
    output_tokens: int
    provider: str


class ChatModel(Protocol):
    def generate(self, request: ChatRequest) -> ChatReply: ...


class AcmeAdapter:
    def __init__(self, client: AcmeClient) -> None:
        self._client = client

    def generate(self, request: ChatRequest) -> ChatReply:
        try:
            raw = self._client.create_completion(
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
            )
        except (ConnectionError, TimeoutError) as exc:
            raise ModelUnavailable("acme") from exc
        return ChatReply(
            raw["choices"][0]["message"]["content"],
            raw["usage"]["prompt_tokens"],
            raw["usage"]["completion_tokens"],
            "acme",
        )


class NimbusAdapter:
    def __init__(self, client: NimbusClient) -> None:
        self._client = client

    def generate(self, request: ChatRequest) -> ChatReply:
        try:
            r = self._client.generate(request.prompt, request.max_tokens)
        except (ConnectionError, TimeoutError) as exc:
            raise ModelUnavailable("nimbus") from exc
        return ChatReply(r.output, r.tokens_in, r.tokens_out, "nimbus")


class FallbackChatModel:
    def __init__(self, models: Sequence[ChatModel]) -> None:
        if not models:
            raise ValueError("at least one model required")
        self._models = tuple(models)

    def generate(self, request: ChatRequest) -> ChatReply:
        last: ModelUnavailable | None = None
        for model in self._models:
            try:
                return model.generate(request)
            except ModelUnavailable as exc:
                last = exc
        raise ModelUnavailable("all providers failed") from last

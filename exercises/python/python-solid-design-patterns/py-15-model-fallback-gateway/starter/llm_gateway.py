from __future__ import annotations

from typing import Protocol, Sequence

from vendors import AcmeClient, NimbusClient


class ModelUnavailable(Exception):
    """Provider-neutral failure: the model could not be reached. Given."""


# TODO: make this a frozen dataclass with slots: prompt: str, max_tokens: int = 256
class ChatRequest:
    ...


# TODO: make this a frozen dataclass with slots: text, input_tokens, output_tokens, provider
class ChatReply:
    ...


class ChatModel(Protocol):
    """Anything with generate(request) -> ChatReply. Given."""

    def generate(self, request: ChatRequest) -> ChatReply: ...


class AcmeAdapter:
    """ChatModel over AcmeClient. Reply provider is "acme".

    Send the prompt as one {"role": "user", "content": prompt} message with
    max_tokens=request.max_tokens. ConnectionError and TimeoutError become
    ModelUnavailable, chained with ``raise ... from``. Other exceptions pass through.
    """

    def __init__(self, client: AcmeClient) -> None:
        raise NotImplementedError("Store the client")

    def generate(self, request: ChatRequest) -> ChatReply:
        raise NotImplementedError("Call the client and normalise the reply")


class NimbusAdapter:
    """ChatModel over NimbusClient. Reply provider is "nimbus".

    Call client.generate(request.prompt, request.max_tokens). Map output, tokens_in
    and tokens_out. Translate ConnectionError and TimeoutError like AcmeAdapter.
    """

    def __init__(self, client: NimbusClient) -> None:
        raise NotImplementedError("Store the client")

    def generate(self, request: ChatRequest) -> ChatReply:
        raise NotImplementedError("Call the client and normalise the reply")


class FallbackChatModel:
    """A ChatModel that tries an ordered sequence of ChatModels.

    - an empty sequence raises ValueError
    - returns the first successful reply (later models are not called)
    - if every model raises ModelUnavailable, raise ModelUnavailable("all providers failed")
      chained to the last failure
    - any other exception propagates immediately
    """

    def __init__(self, models: Sequence[ChatModel]) -> None:
        raise NotImplementedError("Validate and store the models")

    def generate(self, request: ChatRequest) -> ChatReply:
        raise NotImplementedError("Try each model in order")

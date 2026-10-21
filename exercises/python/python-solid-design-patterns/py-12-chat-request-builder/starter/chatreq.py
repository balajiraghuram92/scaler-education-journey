from dataclasses import dataclass
from typing import Any, Self


def estimate_tokens(text: str) -> int:
    """Crude estimate: ``max(1, len(text) // 4)``."""
    raise NotImplementedError("Implement estimate_tokens")


@dataclass(frozen=True, slots=True)
class ChatRequest:
    model: str
    messages: tuple[tuple[str, str], ...]
    temperature: float
    max_tokens: int

    @staticmethod
    def builder(context_window: int = 8192) -> "ChatRequestBuilder":
        """Return a new ChatRequestBuilder with the given context window."""
        raise NotImplementedError("Implement ChatRequest.builder")

    def to_builder(self, context_window: int = 8192) -> "ChatRequestBuilder":
        """Return a builder pre-filled from this request (copy-with-change for retries)."""
        raise NotImplementedError("Implement to_builder")

    def to_payload(self) -> dict[str, Any]:
        """Return a FRESH dict on every call:
        ``{"model", "messages": [{"role", "content"}, ...], "temperature", "max_tokens"}``."""
        raise NotImplementedError("Implement to_payload")


class ChatRequestBuilder:
    """Fluent builder. Setters: model, system, user, assistant, temperature, max_tokens.

    system/user/assistant APPEND a message in call order. Defaults: temperature 0.2,
    max_tokens 512.

    ``build()`` raises ValueError when:
      - model is missing (mention ``model``)
      - there is no user message (mention ``user message``)
      - the system message is not first (mention ``first``)
      - there is more than one system message (mention ``only one``)
      - temperature is outside 0..2 (mention ``temperature``)
      - max_tokens < 1
      - estimated prompt tokens + max_tokens exceed the context window
        (mention ``context window``). This is checked in ``build()``, so it does
        not depend on the order the setters were called.

    Messages are stored as a tuple; two builds are independent objects.
    """

    def __init__(self, context_window: int = 8192) -> None:
        raise NotImplementedError("Implement the constructor")

    def model(self, name: str) -> Self:
        raise NotImplementedError("Implement model")

    def system(self, text: str) -> Self:
        raise NotImplementedError("Implement system")

    def user(self, text: str) -> Self:
        raise NotImplementedError("Implement user")

    def assistant(self, text: str) -> Self:
        raise NotImplementedError("Implement assistant")

    def temperature(self, value: float) -> Self:
        raise NotImplementedError("Implement temperature")

    def max_tokens(self, value: int) -> Self:
        raise NotImplementedError("Implement max_tokens")

    def build(self) -> ChatRequest:
        raise NotImplementedError("Implement build")

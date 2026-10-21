from dataclasses import dataclass
from typing import Any, Self


def estimate_tokens(text: str) -> int:
    """Crude estimate: about four characters per token, at least one."""
    return max(1, len(text) // 4)


@dataclass(frozen=True, slots=True)
class ChatRequest:
    model: str
    messages: tuple[tuple[str, str], ...]
    temperature: float
    max_tokens: int

    @staticmethod
    def builder(context_window: int = 8192) -> "ChatRequestBuilder":
        return ChatRequestBuilder(context_window)

    def to_builder(self, context_window: int = 8192) -> "ChatRequestBuilder":
        """Start a new builder pre-filled from this request (copy-with-change)."""
        builder = ChatRequestBuilder(context_window)
        builder._model = self.model
        builder._messages = list(self.messages)
        builder._temperature = self.temperature
        builder._max_tokens = self.max_tokens
        return builder

    def to_payload(self) -> dict[str, Any]:
        """A fresh dict every call, so callers cannot corrupt the request."""
        return {
            "model": self.model,
            "messages": [{"role": r, "content": c} for r, c in self.messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class ChatRequestBuilder:
    def __init__(self, context_window: int = 8192) -> None:
        self._context_window = context_window
        self._model: str | None = None
        self._messages: list[tuple[str, str]] = []
        self._temperature = 0.2
        self._max_tokens = 512

    def model(self, name: str) -> Self:
        self._model = name
        return self

    def system(self, text: str) -> Self:
        self._messages.append(("system", text))
        return self

    def user(self, text: str) -> Self:
        self._messages.append(("user", text))
        return self

    def assistant(self, text: str) -> Self:
        self._messages.append(("assistant", text))
        return self

    def temperature(self, value: float) -> Self:
        self._temperature = value
        return self

    def max_tokens(self, value: int) -> Self:
        self._max_tokens = value
        return self

    def build(self) -> ChatRequest:
        if not self._model:
            raise ValueError("model is required")
        roles = [role for role, _ in self._messages]
        if "user" not in roles:
            raise ValueError("at least one user message is required")
        if "system" in roles and roles.index("system") != 0:
            raise ValueError("system message must come first")
        if roles.count("system") > 1:
            raise ValueError("only one system message is allowed")
        if not 0.0 <= self._temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if self._max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        prompt_tokens = sum(estimate_tokens(text) for _, text in self._messages)
        if prompt_tokens + self._max_tokens > self._context_window:
            raise ValueError(
                f"prompt (~{prompt_tokens}) + max_tokens ({self._max_tokens}) "
                f"exceeds context window {self._context_window}"
            )
        return ChatRequest(self._model, tuple(self._messages), self._temperature, self._max_tokens)

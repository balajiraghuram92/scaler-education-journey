"""Provider protocols. Every call returns token counts and latency."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ChatResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


@dataclass(frozen=True)
class EmbeddingResult:
    vector: list[float]
    tokens: int
    latency_ms: int


class ChatProvider(Protocol):
    name: str

    async def chat(self, messages: list[ChatMessage], *, json_mode: bool = False) -> ChatResult:
        """Complete a chat; json_mode requests a JSON-object response."""
        ...

    async def close(self) -> None:
        """Release owned resources (no-op for providers without any)."""
        ...


class EmbeddingProvider(Protocol):
    name: str
    dimensions: int

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed each text; results align 1:1 with the inputs."""
        ...

    async def close(self) -> None:
        """Release owned resources (no-op for providers without any)."""
        ...

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class ProviderError(Exception):
    """Transient provider failure: timeout, 5xx, rate limit."""


class ChatModel(Protocol):
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion: ...


class FallbackChat:
    """Try each model in order; only ProviderError triggers the next one.

    - Same ``complete`` signature as ChatModel, so it can be used anywhere a
      single model can (Liskov substitution).
    - Return the first successful Completion. Later models are not called.
    - Any exception other than ProviderError propagates immediately.
    - If every model raises ProviderError, raise
      ``ExceptionGroup("all providers failed", errors)`` holding every cause.
    - An empty ``models`` sequence raises ValueError at construction.
    """

    def __init__(self, models: Sequence[ChatModel]) -> None:
        raise NotImplementedError("Implement the constructor")

    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        raise NotImplementedError("Implement complete")


def contract_violations(model: ChatModel) -> list[str]:
    """Return human-readable contract violations; an empty list means compliant.

    Call ``model.complete("ping")`` with the default, with ``max_tokens=1`` and
    with ``max_tokens=4096``. A ProviderError is allowed. Any other exception,
    or a result that is not a Completion with str ``text``, adds a message that
    starts with the label of the call: ``default``, ``max_tokens=1`` or
    ``max_tokens=4096``.
    """
    raise NotImplementedError("Implement contract_violations")

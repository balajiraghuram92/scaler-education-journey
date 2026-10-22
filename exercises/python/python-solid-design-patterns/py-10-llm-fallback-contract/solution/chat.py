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
    """Try each model in order; only ProviderError triggers the next one."""

    def __init__(self, models: Sequence[ChatModel]) -> None:
        if not models:
            raise ValueError("at least one model is required")
        self._models = tuple(models)

    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        errors: list[Exception] = []
        for model in self._models:
            try:
                return model.complete(prompt, max_tokens=max_tokens)
            except ProviderError as exc:
                errors.append(exc)
        raise ExceptionGroup("all providers failed", errors)


def contract_violations(model: ChatModel) -> list[str]:
    """Return human-readable contract violations; an empty list means compliant.

    Contract: complete() accepts the default and any max_tokens in 1..4096,
    returns a Completion whose text is a str, and may raise only ProviderError.
    """
    problems: list[str] = []
    for label, kwargs in (("default", {}), ("max_tokens=1", {"max_tokens": 1}),
                          ("max_tokens=4096", {"max_tokens": 4096})):
        try:
            result = model.complete("ping", **kwargs)
        except ProviderError:
            continue
        except Exception as exc:
            problems.append(f"{label}: raised {type(exc).__name__}")
            continue
        if not isinstance(result, Completion) or not isinstance(result.text, str):
            problems.append(f"{label}: did not return a Completion with str text")
    return problems

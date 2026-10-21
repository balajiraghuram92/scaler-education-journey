from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)

MAX_ERROR_CHARS = 500
MAX_ECHO_CHARS = 2000


@dataclass(frozen=True, slots=True)
class Completion:
    text: str
    finish_reason: str  # "stop", "length", "content_filter", ...


Complete = Callable[[list[dict[str, str]], int], Awaitable[Completion]]  # (messages, max_tokens)


@dataclass(slots=True)
class GenStats:
    attempts: int = 0
    repairs: int = 0
    truncations: int = 0


class TruncatedOutput(Exception):
    """Output was cut off by the token cap and the cap cannot grow further."""


class StructuredOutputError(Exception):
    """Invalid content after the repair budget, or an unusable finish reason."""


def extract_json(text: str) -> str:
    """Return the first balanced JSON object in ``text``.

    - strip an optional markdown fence (```json ... ```)
    - ignore braces inside strings and honour escaped quotes
    - raise ``ValueError`` if there is no object or it is unbalanced
    """
    raise NotImplementedError("Implement extract_json")


async def generate_validated(
    complete: Complete,
    messages: list[dict[str, str]],
    model: type[M],
    *,
    max_tokens: int = 256,
    max_tokens_cap: int = 1024,
    max_repairs: int = 2,
    stats: GenStats | None = None,
) -> M:
    """Validate-and-repair loop around ``complete(messages, max_tokens) -> Completion``.

    - ``stats.attempts`` counts every call to ``complete``
    - ``finish_reason == "length"``: count a truncation, double ``max_tokens`` up to
      ``max_tokens_cap`` and retry the SAME messages (no repair message, no repair spent);
      already at the cap -> ``TruncatedOutput``
    - any other reason than ``"stop"``: ``StructuredOutputError`` immediately (message names the reason)
    - invalid content (parse or validation error): if ``repairs >= max_repairs`` raise
      ``StructuredOutputError("invalid after N repairs: ...")``; otherwise append the assistant
      text (cut to MAX_ECHO_CHARS) and a user message with the error summary (cut to
      MAX_ERROR_CHARS) and try again
    - never mutate the caller's ``messages`` list
    """
    raise NotImplementedError("Implement generate_validated")

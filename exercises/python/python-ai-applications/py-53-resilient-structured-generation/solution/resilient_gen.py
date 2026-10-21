from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError

M = TypeVar("M", bound=BaseModel)

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
MAX_ERROR_CHARS = 500
MAX_ECHO_CHARS = 2000


@dataclass(frozen=True, slots=True)
class Completion:
    text: str
    finish_reason: str          # "stop", "length", "content_filter", ...


Complete = Callable[[list[dict[str, str]], int], Awaitable[Completion]]   # (messages, max_tokens)


@dataclass(slots=True)
class GenStats:
    attempts: int = 0
    repairs: int = 0
    truncations: int = 0


class TruncatedOutput(Exception):
    """Output was cut off by the token cap and the cap cannot grow further."""


class StructuredOutputError(Exception):
    pass


def extract_json(text: str) -> str:
    if (m := _FENCE.search(text)):
        text = m.group(1)
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object found")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("unbalanced JSON object")


def summarise(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        text = "; ".join(f"{'.'.join(map(str, e['loc'])) or '<root>'}: {e['msg']}"
                         for e in exc.errors(include_url=False))
    else:
        text = str(exc)
    return text[:MAX_ERROR_CHARS]


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
    stats = stats if stats is not None else GenStats()
    convo = list(messages)
    last_error = ""
    while True:
        stats.attempts += 1
        completion = await complete(convo, max_tokens)

        if completion.finish_reason == "length":
            stats.truncations += 1
            if max_tokens >= max_tokens_cap:
                raise TruncatedOutput(f"still truncated at max_tokens={max_tokens}")
            max_tokens = min(max_tokens * 2, max_tokens_cap)      # same prompt, bigger cap
            continue
        if completion.finish_reason != "stop":
            raise StructuredOutputError(f"unusable finish_reason {completion.finish_reason!r}")

        try:
            return model.model_validate_json(extract_json(completion.text))
        except ValueError as exc:                                  # includes ValidationError
            last_error = summarise(exc)
        if stats.repairs >= max_repairs:
            raise StructuredOutputError(f"invalid after {stats.repairs} repairs: {last_error}")
        stats.repairs += 1
        convo += [
            {"role": "assistant", "content": completion.text[:MAX_ECHO_CHARS]},
            {"role": "user", "content": f"Invalid: {last_error}. Reply with only the corrected JSON."},
        ]

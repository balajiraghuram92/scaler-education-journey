from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypedDict, TypeIs, assert_never


# TODO: make Ok and Err frozen, slotted dataclasses (immutable value objects).
@dataclass
class Ok[T]:
    value: T


@dataclass
class Err[E]:
    error: E


# TODO: define ``type Result[T, E] = Ok[T] | Err[E]`` (PEP 695 type alias).
type Result[T, E] = Ok[T] | Err[E]


def is_ok[T, E](r: Result[T, E]) -> TypeIs[Ok[T]]:
    """Return True for ``Ok``; written as a TypeIs guard so both branches narrow."""
    raise NotImplementedError("Implement is_ok")


def map_result[T, U, E](r: Result[T, E], fn: Callable[[T], U]) -> Result[U, E]:
    """Apply ``fn`` to the value of an ``Ok``; pass an ``Err`` through unchanged
    (the very same object). Use ``match`` with class patterns."""
    raise NotImplementedError("Implement map_result")


def unwrap_or[T, D](r: Result[T, object], default: D) -> T | D:
    """Return the value of an ``Ok``, otherwise ``default``."""
    raise NotImplementedError("Implement unwrap_or")


def parse_int(text: str) -> Result[int, str]:
    """``Ok(int(text))`` or ``Err(f"not an int: {text!r}")`` when parsing fails."""
    raise NotImplementedError("Implement parse_int")


class TokenEvent(TypedDict):
    type: Literal["token"]
    text: str


class ToolEvent(TypedDict):
    type: Literal["tool_call"]
    name: str
    arguments: dict[str, object]


class DoneEvent(TypedDict):
    type: Literal["done"]
    finish_reason: str


type Event = TokenEvent | ToolEvent | DoneEvent


def describe(event: Event) -> str:
    """Return ``"token"``, ``"tool"`` or ``"done"`` using an if/elif chain on
    ``event["type"]`` that ends with ``assert_never(event)`` in the ``else``.

    Type-checking (``mypy --strict``) is a self-check; the hidden tests grade runtime behaviour.
    """
    raise NotImplementedError("Implement describe")

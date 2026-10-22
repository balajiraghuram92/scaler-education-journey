from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypedDict, TypeIs, assert_never


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E


type Result[T, E] = Ok[T] | Err[E]


def is_ok[T, E](r: Result[T, E]) -> TypeIs[Ok[T]]:
    return isinstance(r, Ok)


def map_result[T, U, E](r: Result[T, E], fn: Callable[[T], U]) -> Result[U, E]:
    match r:
        case Ok(value):
            return Ok(fn(value))
        case Err():
            return r


def unwrap_or[T, D](r: Result[T, object], default: D) -> T | D:
    return r.value if isinstance(r, Ok) else default


def parse_int(text: str) -> Result[int, str]:
    try:
        return Ok(int(text))
    except ValueError:
        return Err(f"not an int: {text!r}")


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
    if event["type"] == "token":
        return "token"
    elif event["type"] == "tool_call":
        return "tool"
    elif event["type"] == "done":
        return "done"
    else:
        assert_never(event)

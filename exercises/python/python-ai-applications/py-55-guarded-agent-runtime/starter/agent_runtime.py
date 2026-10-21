from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

from pydantic import BaseModel


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: str  # raw JSON text produced by the model


@dataclass(frozen=True, slots=True)
class ModelReply:
    text: str | None = None
    tool_call: ToolCall | None = None
    tokens: int = 0


class Model(Protocol):
    async def next(self, messages: list[dict]) -> ModelReply: ...


Handler = Callable[[BaseModel], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    args: type[BaseModel]
    handler: Handler
    timeout_s: float = 5.0
    needs_approval: bool = False
    max_calls: int | None = None  # per run


class Registry:
    def __init__(self) -> None:
        self.tools: dict[str, ToolSpec] = {}

    def add(self, spec: ToolSpec) -> None:
        """Register ``spec`` under ``spec.name`` in ``self.tools``."""
        raise NotImplementedError("Implement Registry.add")


StopReason = Literal["final", "max_steps", "budget", "loop", "deadline", "tool_cap"]


@dataclass(slots=True)
class RunResult:
    answer: str | None
    stop_reason: StopReason
    steps: int
    tokens: int
    trace: list[dict[str, str]] = field(default_factory=list)


def canonical(arguments: str) -> str:
    """Parse JSON and re-dump with sorted keys and compact separators (``(",", ":")``).
    Return the raw text unchanged when it is not valid JSON."""
    raise NotImplementedError("Implement canonical")


async def execute_tool(registry: Registry, call: ToolCall, approve: Callable[[ToolCall], bool],
                       max_observation_chars: int) -> str:
    """Run one tool call and return an observation string. NEVER raises.

    - unknown tool: ``ERROR unknown tool 'x'. Available: a, b`` (names sorted)
    - invalid arguments (``model_validate_json``): ``ERROR invalid arguments at <loc>: <msg>`` for the first error
    - ``needs_approval`` and ``approve(call)`` is false: ``ERROR denied: ...``
    - timeout (``asyncio.timeout(spec.timeout_s)``): ``ERROR tool 'x' timed out after <s>s``
    - handler exception: ``ERROR tool 'x' failed (ExcName)`` with no exception text
    - observations longer than ``max_observation_chars`` are cut and end with ``...[truncated]``
    """
    raise NotImplementedError("Implement execute_tool")


async def run_agent(
    model: Model,
    registry: Registry,
    question: str,
    *,
    max_steps: int = 8,
    token_budget: int = 4000,
    max_repeats: int = 2,
    deadline_s: float = 30.0,
    max_observation_chars: int = 2000,
    approve: Callable[[ToolCall], bool] = lambda call: False,
    clock: Callable[[], float] = time.monotonic,
) -> RunResult:
    """Think, act, observe loop that always ends with an explicit stop reason.

    Per step, in this order: (1) deadline via the injected ``clock`` -> ``deadline``;
    (2) ``await model.next(messages)``; (3) add the reply's tokens and stop with ``budget`` when over
    ``token_budget`` (BEFORE any tool runs); (4) no tool call -> ``final`` with the reply text;
    (5) loop detection on ``(name, canonical(arguments))`` counts: more than ``max_repeats`` -> ``loop``;
    (6) per-tool ``max_calls`` cap -> ``tool_cap``; (7) execute the tool, append
    ``{"tool", "arguments" (canonical), "observation"}`` to ``trace`` and extend ``messages``
    (assistant tool call, then a ``role: "tool"`` message with the observation).
    After ``max_steps`` steps stop with ``max_steps``. ``steps`` counts steps started.
    """
    raise NotImplementedError("Implement run_agent")

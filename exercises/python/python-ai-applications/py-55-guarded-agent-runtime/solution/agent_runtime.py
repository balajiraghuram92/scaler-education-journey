from __future__ import annotations

import asyncio
import json
import time
from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

from pydantic import BaseModel, ValidationError


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: str


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
    max_calls: int | None = None          # per run


class Registry:
    def __init__(self) -> None:
        self.tools: dict[str, ToolSpec] = {}

    def add(self, spec: ToolSpec) -> None:
        self.tools[spec.name] = spec


def canonical(arguments: str) -> str:
    """Same call, same key: parse and re-serialise with sorted keys; fall back to the raw text."""
    try:
        return json.dumps(json.loads(arguments), sort_keys=True, separators=(",", ":"))
    except ValueError:
        return arguments


StopReason = Literal["final", "max_steps", "budget", "loop", "deadline", "tool_cap"]


@dataclass(slots=True)
class RunResult:
    answer: str | None
    stop_reason: StopReason
    steps: int
    tokens: int
    trace: list[dict[str, str]] = field(default_factory=list)


async def execute_tool(registry: Registry, call: ToolCall, approve: Callable[[ToolCall], bool],
                       max_observation_chars: int) -> str:
    spec = registry.tools.get(call.name)
    if spec is None:
        return f"ERROR unknown tool {call.name!r}. Available: {', '.join(sorted(registry.tools))}"
    try:
        args = spec.args.model_validate_json(call.arguments)
    except ValidationError as exc:
        e = exc.errors(include_url=False)[0]
        return f"ERROR invalid arguments at {'.'.join(map(str, e['loc']))}: {e['msg']}"
    if spec.needs_approval and not approve(call):
        return "ERROR denied: a human reviewer did not approve this action"
    try:
        async with asyncio.timeout(spec.timeout_s):
            observation = await spec.handler(args)
    except TimeoutError:
        return f"ERROR tool {call.name!r} timed out after {spec.timeout_s}s"
    except Exception as exc:
        return f"ERROR tool {call.name!r} failed ({type(exc).__name__})"
    if len(observation) > max_observation_chars:
        observation = observation[:max_observation_chars] + "...[truncated]"
    return observation


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
    started = clock()
    messages: list[dict] = [{"role": "system", "content": "Use tools when needed."},
                            {"role": "user", "content": question}]
    repeats: Counter[tuple[str, str]] = Counter()
    per_tool: Counter[str] = Counter()
    result = RunResult(None, "max_steps", 0, 0)
    for step in range(1, max_steps + 1):
        result.steps = step
        if clock() - started > deadline_s:
            result.stop_reason = "deadline"
            return result
        reply = await model.next(messages)
        result.tokens += reply.tokens
        if result.tokens > token_budget:
            result.stop_reason = "budget"
            return result
        call = reply.tool_call
        if call is None:
            result.answer, result.stop_reason = reply.text, "final"
            return result
        key = (call.name, canonical(call.arguments))
        repeats[key] += 1
        if repeats[key] > max_repeats:
            result.stop_reason = "loop"
            return result
        spec = registry.tools.get(call.name)
        if spec and spec.max_calls is not None and per_tool[call.name] >= spec.max_calls:
            result.stop_reason = "tool_cap"
            return result
        per_tool[call.name] += 1
        observation = await execute_tool(registry, call, approve, max_observation_chars)
        result.trace.append({"tool": call.name, "arguments": key[1], "observation": observation})
        messages += [{"role": "assistant", "content": None,
                      "tool_call": {"id": call.id, "name": call.name, "arguments": call.arguments}},
                     {"role": "tool", "tool_call_id": call.id, "content": observation}]
    return result

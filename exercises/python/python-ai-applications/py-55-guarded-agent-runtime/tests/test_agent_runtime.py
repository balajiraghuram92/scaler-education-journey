import asyncio
import json

import pytest
from pydantic import BaseModel, ConfigDict, Field

from agent_runtime import (
    ModelReply,
    Registry,
    ToolCall,
    ToolSpec,
    canonical,
    run_agent,
)


class OrderArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str = Field(pattern=r"^ord_[a-z0-9]{4}$")


async def get_order(args: OrderArgs) -> str:
    return f"order {args.order_id}: delivered"


async def big(args: OrderArgs) -> str:
    return "x" * 5000


async def boom(args: OrderArgs) -> str:
    raise RuntimeError("secret database password")


async def slow(args: OrderArgs) -> str:
    await asyncio.sleep(1)
    return "never"


def make_registry() -> Registry:
    reg = Registry()
    reg.add(ToolSpec("get_order", OrderArgs, get_order, max_calls=3))
    reg.add(ToolSpec("big", OrderArgs, big))
    reg.add(ToolSpec("slow", OrderArgs, slow, timeout_s=0.05))
    reg.add(ToolSpec("boom", OrderArgs, boom))
    reg.add(ToolSpec("refund", OrderArgs, get_order, needs_approval=True))
    return reg


class Script:
    def __init__(self, *replies: ModelReply) -> None:
        self.replies = list(replies)
        self.seen: list[list[dict]] = []

    async def next(self, messages):
        self.seen.append(list(messages))
        return self.replies.pop(0)


def call(name, args, tokens=10, id="c"):
    text = args if isinstance(args, str) else json.dumps(args)
    return ModelReply(tool_call=ToolCall(id, name, text), tokens=tokens)


def final(text="done", tokens=10):
    return ModelReply(text=text, tokens=tokens)


def run(model, **kw):
    return asyncio.run(run_agent(model, make_registry(), "q", **kw))


def test_canonical_ignores_key_order_and_whitespace():
    assert canonical('{"b": 2, "a": 1}') == canonical('{"a":1,"b":2}') == '{"a":1,"b":2}'
    assert canonical("not json") == "not json", "invalid JSON falls back to the raw text"


def test_happy_path():
    r = run(Script(call("get_order", {"order_id": "ord_a1b2"}), final("ok")))
    assert (r.stop_reason, r.steps, r.answer) == ("final", 2, "ok")
    assert r.trace[0]["observation"] == "order ord_a1b2: delivered"
    assert r.trace[0]["tool"] == "get_order" and r.trace[0]["arguments"] == '{"order_id":"ord_a1b2"}'
    assert r.tokens == 20


def test_loop_detection_survives_whitespace_and_key_order():
    same_a = call("get_order", '{"order_id":"ord_a1b2"}')
    same_b = call("get_order", '{ "order_id" : "ord_a1b2" }')
    r = run(Script(same_a, same_b, same_a, final()), max_repeats=2)
    assert r.stop_reason == "loop" and len(r.trace) == 2


def test_per_tool_call_cap_applies_to_different_arguments():
    replies = [call("get_order", {"order_id": f"ord_{i:04d}"}) for i in range(5)]
    r = run(Script(*replies), max_steps=10)
    assert r.stop_reason == "tool_cap" and len(r.trace) == 3


def test_budget_is_checked_before_the_tool_runs():
    r = run(Script(call("get_order", {"order_id": "ord_a1b2"}, tokens=900),
                   call("get_order", {"order_id": "ord_a1b3"}, tokens=900),
                   call("get_order", {"order_id": "ord_a1b4"}, tokens=900)), token_budget=2000)
    assert (r.stop_reason, r.steps, r.tokens, len(r.trace)) == ("budget", 3, 2700, 2)


def test_deadline_uses_the_injected_clock():
    ticks = iter([0.0, 1.0, 100.0])
    r = run(Script(call("get_order", {"order_id": "ord_a1b2"}), final()),
            deadline_s=30.0, clock=lambda: next(ticks))
    assert r.stop_reason == "deadline" and r.steps == 2 and len(r.trace) == 1


def test_errors_are_observations_not_exceptions():
    script = Script(call("nope", {}), call("get_order", {"order_id": "BAD"}),
                    call("slow", {"order_id": "ord_a1b2"}), call("refund", {"order_id": "ord_a1b2"}),
                    call("boom", {"order_id": "ord_a1b2"}), final("gave up"))
    r = run(script)
    obs = [t["observation"] for t in r.trace]
    assert obs[0].startswith("ERROR unknown tool 'nope'. Available: ")
    assert obs[1].startswith("ERROR invalid arguments at order_id")
    assert obs[2].startswith("ERROR tool 'slow' timed out")
    assert obs[3].startswith("ERROR denied")
    assert obs[4] == "ERROR tool 'boom' failed (RuntimeError)", "name the exception type, never its text"
    assert "secret" not in obs[4]
    assert r.answer == "gave up"


def test_approval_callback_allows_the_tool():
    r = run(Script(call("refund", {"order_id": "ord_a1b2"}), final()), approve=lambda c: True)
    assert r.trace[0]["observation"] == "order ord_a1b2: delivered"


def test_long_observations_are_truncated_before_entering_history():
    script = Script(call("big", {"order_id": "ord_a1b2"}), final())
    r = run(script, max_observation_chars=100)
    assert r.trace[0]["observation"].endswith("...[truncated]") and len(r.trace[0]["observation"]) < 130
    assert len(script.seen[1][-1]["content"]) < 130


def test_max_steps():
    replies = [call("get_order", {"order_id": f"ord_{i:04d}"}) for i in range(2)] + [final()]
    r = run(Script(*replies), max_steps=2)
    assert r.stop_reason == "max_steps" and r.steps == 2

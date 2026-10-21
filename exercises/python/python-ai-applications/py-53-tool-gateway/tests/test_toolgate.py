import dataclasses
import logging

import pytest
from pydantic import BaseModel, ConfigDict, Field

from toolgate import Ctx, Observation, Tool, ToolRegistry


class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=100)
    limit: int = Field(5, ge=1, le=20)


class CancelArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str = Field(pattern=r"^ord_[a-z0-9]{8}$")


class LooseArgs(BaseModel):
    x: int


calls: list[str] = []


def search(args, ctx):
    calls.append("search")
    assert isinstance(args, SearchArgs), "the handler must receive the validated model"
    return f"[{ctx.tenant_id}] results for {args.query!r} (limit {args.limit})"


def cancel(args, ctx):
    calls.append("cancel")
    return f"cancelled {args.order_id}"


def boom(args, ctx):
    raise RuntimeError("db password is hunter2")


@pytest.fixture
def registry():
    calls.clear()
    reg = ToolRegistry()
    reg.register(Tool("search_orders", "Search orders.", SearchArgs, search, "orders:read"))
    reg.register(Tool("cancel_order", "Cancel an order.", CancelArgs, cancel, "orders:write", needs_approval=True))
    reg.register(Tool("flaky", "Always fails.", SearchArgs, boom, "orders:read"))
    return reg


READER = Ctx("t1", frozenset({"orders:read"}))
WRITER = Ctx("t1", frozenset({"orders:read", "orders:write"}))


def test_definitions_are_generated_from_models(registry):
    raw = registry.definitions()
    assert all(d["type"] == "function" for d in raw)
    defs = {d["function"]["name"]: d["function"] for d in raw}
    assert set(defs) == {"search_orders", "cancel_order", "flaky"}
    assert defs["search_orders"]["description"] == "Search orders."
    assert defs["search_orders"]["parameters"]["required"] == ["query"]
    assert defs["cancel_order"]["parameters"]["additionalProperties"] is False


def test_ok_path_uses_session_tenant(registry):
    obs = registry.call("search_orders", '{"query": "shoes"}', READER)
    assert obs.status == "ok" and obs.content == "[t1] results for 'shoes' (limit 5)"


def test_unknown_tool_lists_available_names(registry):
    obs = registry.call("drop_tables", "{}", WRITER)
    assert obs.status == "unknown_tool"
    assert "cancel_order, flaky, search_orders" in obs.content, "available names, sorted"


def test_scope_is_checked_before_arguments_are_parsed(registry):
    obs = registry.call("cancel_order", "not even json", READER)
    assert obs.status == "forbidden"
    assert "json" not in obs.content.lower(), "a caller without the scope must learn nothing about the arguments"
    obs = registry.call("cancel_order", '{"order_id": "ord_ab12cd34"}', READER, approved=True)
    assert obs.status == "forbidden", "approval must not bypass the scope check"
    assert calls == []


@pytest.mark.parametrize(
    "arguments",
    [
        '{"query": ""}',
        '{"query": "ok", "limit": 99}',
        '{"query": "ok", "tenant_id": "t2"}',
        "[]",
        "not json",
    ],
    ids=["empty-query", "limit-too-big", "extra-field", "not-an-object", "not-json"],
)
def test_bad_arguments_never_reach_the_handler(registry, arguments):
    obs = registry.call("search_orders", arguments, READER)
    assert obs.status == "invalid_arguments"
    assert calls == []


def test_error_summary_is_capped_at_three_problems(registry):
    obs = registry.call("search_orders", '{"query": "", "limit": 0, "a": 1, "b": 2, "c": 3}', READER)
    assert obs.status == "invalid_arguments"
    assert obs.content.count(";") == 2, "exactly three problems joined by '; '"
    assert all(": " in part for part in obs.content.split(";")), "format each problem as 'loc: message'"


def test_destructive_tool_needs_approval_and_runs_once_approved(registry):
    first = registry.call("cancel_order", '{"order_id": "ord_ab12cd34"}', WRITER)
    assert first.status == "needs_approval" and calls == []
    bad = registry.call("cancel_order", '{"order_id": "nope"}', WRITER, approved=True)
    assert bad.status == "invalid_arguments", "approval does not skip validation"
    second = registry.call("cancel_order", '{"order_id": "ord_ab12cd34"}', WRITER, approved=True)
    assert second.status == "ok" and calls == ["cancel"]


def test_handler_exceptions_do_not_leak_details(registry, caplog):
    with caplog.at_level(logging.ERROR):
        obs = registry.call("flaky", '{"query": "x"}', READER)
    assert obs.status == "error"
    assert obs.content == "tool 'flaky' failed"
    assert "hunter2" not in obs.content
    assert any(r.exc_info for r in caplog.records), "log the exception server-side"


def test_registration_rules_and_frozen_dataclasses(registry):
    with pytest.raises(ValueError):
        registry.register(Tool("search_orders", "dup", SearchArgs, search, "orders:read"))
    with pytest.raises(ValueError):
        registry.register(Tool("loose", "no forbid", LooseArgs, search, "orders:read"))
    for obj, field in ((READER, "tenant_id"), (Observation("ok", "x"), "status"), (Tool("t", "d", SearchArgs, search, "s"), "name")):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(obj, field, "changed")
        assert not hasattr(obj, "__dict__"), "dataclasses must be slotted"

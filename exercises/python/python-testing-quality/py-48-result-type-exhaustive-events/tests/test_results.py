import dataclasses
from typing import assert_type

import pytest

from results import (
    DoneEvent, Err, Event, Ok, Result, TokenEvent, ToolEvent,
    describe, is_ok, map_result, parse_int, unwrap_or,
)


def test_parse_int_ok_and_err():
    assert parse_int("42") == Ok(42)
    assert parse_int("x") == Err("not an int: 'x'")


def test_parse_int_edge_inputs():
    assert parse_int(" 7 ") == Ok(7)
    assert parse_int("-3") == Ok(-3)
    assert parse_int("") == Err("not an int: ''")
    assert parse_int("3.5") == Err("not an int: '3.5'")


def test_map_result_applies_only_on_ok():
    assert map_result(Ok(2), lambda n: n * 10) == Ok(20)
    failed: Result[int, str] = Err("boom")
    mapped = map_result(failed, lambda n: n * 10)
    assert mapped == Err("boom")
    assert mapped is failed, "an Err must be passed through unchanged (same object)"


def test_map_result_does_not_call_fn_for_err():
    called: list[int] = []
    map_result(Err("e"), lambda n: called.append(n))
    assert called == [], "fn must not run for an Err"


def test_is_ok_narrows_for_the_checker():
    r = parse_int("7")
    if is_ok(r):
        assert_type(r, Ok[int])
        assert r.value == 7
    else:
        pytest.fail("expected Ok")
    bad = parse_int("x")
    assert is_ok(bad) is False
    assert is_ok(Ok(0)) is True


def test_unwrap_or_default_union():
    assert unwrap_or(parse_int("5"), 0) == 5
    assert unwrap_or(parse_int("x"), None) is None
    assert unwrap_or(Ok(0), 99) == 0, "a falsy Ok value is still a value"


def test_results_are_immutable_slotted_values():
    ok = Ok(1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ok.value = 2
    with pytest.raises(dataclasses.FrozenInstanceError):
        Err("e").error = "other"
    assert {Ok(1), Ok(1)} == {Ok(1)}, "frozen dataclasses are hashable by value"
    assert not hasattr(ok, "__dict__"), "Ok must use slots"
    assert not hasattr(Err("e"), "__dict__"), "Err must use slots"


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        pytest.param(TokenEvent(type="token", text="hi"), "token", id="token"),
        pytest.param(ToolEvent(type="tool_call", name="search", arguments={}), "tool", id="tool"),
        pytest.param(DoneEvent(type="done", finish_reason="stop"), "done", id="done"),
    ],
)
def test_describe_covers_every_event(event: Event, expected: str):
    assert describe(event) == expected


def test_unknown_event_fails_loudly_at_runtime():
    bogus: Event = {"type": "heartbeat"}  # type: ignore[assignment]
    with pytest.raises(AssertionError):
        describe(bogus)

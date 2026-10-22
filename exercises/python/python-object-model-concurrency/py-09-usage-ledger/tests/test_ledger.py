import dataclasses

import pytest

from ledger import InvalidEvent, LedgerError, Summary, UsageEvent, parse_event, summarize

GOOD = [
    {"tenant": "acme", "tokens": 10},
    {"tenant": "acme", "tokens": 5, "model": "m"},
    {"tenant": "globex", "tokens": 7},
]


def test_aggregates_valid_events():
    s = summarize(GOOD)
    assert s.tokens_by_tenant == {"acme": 15, "globex": 7}
    assert s.errors == ()
    assert type(s.tokens_by_tenant) is dict, "tokens_by_tenant should be a plain dict"
    assert isinstance(s.errors, tuple)


def test_collects_errors_without_stopping():
    raw = [
        {"tenant": "a", "tokens": 1},
        {"tokens": 2},
        {"tenant": "a", "tokens": -1},
        {"tenant": "a", "tokens": True},
        {"tenant": "b", "tokens": 4},
    ]
    s = summarize(raw)
    assert s.tokens_by_tenant == {"a": 1, "b": 4}, "valid events before and after bad ones are all counted"
    assert [e.index for e in s.errors] == [1, 2, 3], "errors carry their position in the input"
    assert all(isinstance(e, InvalidEvent) for e in s.errors)


def test_invalid_event_and_exception_hierarchy():
    err = InvalidEvent(4, "boom")
    assert (err.index, err.reason) == (4, "boom")
    assert str(err) == "event 4: boom"
    assert issubclass(InvalidEvent, LedgerError) and issubclass(LedgerError, Exception)
    assert not issubclass(InvalidEvent, (KeyError, ValueError, TypeError))


def test_parse_event_builds_usage_event_with_default_model():
    e = parse_event({"tenant": "acme", "tokens": 3})
    assert isinstance(e, UsageEvent)
    assert (e.tenant, e.tokens, e.model) == ("acme", 3, "default")
    assert parse_event({"tenant": "acme", "tokens": 0, "model": "m1"}).model == "m1", "zero tokens is valid"


def test_cause_chain_is_preserved():
    with pytest.raises(InvalidEvent) as ei:
        parse_event({"tokens": 1}, 7)
    assert isinstance(ei.value.__cause__, KeyError), "a missing field must chain the original KeyError"
    assert ei.value.index == 7
    with pytest.raises(InvalidEvent) as ei2:
        parse_event({"tenant": "", "tokens": 1})
    assert isinstance(ei2.value.__cause__, ValueError), "a rule violation must chain the ValueError"
    with pytest.raises(InvalidEvent) as ei3:
        parse_event({"tenant": "a", "tokens": -5})
    assert isinstance(ei3.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "raw",
    [
        {"tenant": "a"},
        {"tokens": 1},
        {"tenant": 5, "tokens": 1},
        {"tenant": "a", "tokens": 1, "model": 3},
        {"tenant": "a", "tokens": "10"},
        {"tenant": "a", "tokens": 1.5},
        {"tenant": "a", "tokens": True},
        {"tenant": "", "tokens": 1},
        {"tenant": "a", "tokens": -1},
    ],
)
def test_parse_event_only_raises_invalid_event(raw):
    with pytest.raises(InvalidEvent) as ei:
        parse_event(raw, 2)
    assert ei.value.index == 2, "the index passed to parse_event must be stored on the error"
    assert ei.value.reason, "give a non-empty reason"


def test_usage_event_is_frozen_slotted_kw_only_and_validates():
    e = UsageEvent(tenant="a", tokens=1)
    assert e.model == "default"
    with pytest.raises(dataclasses.FrozenInstanceError):
        e.tokens = 2
    assert not hasattr(e, "__dict__"), "UsageEvent must use __slots__"
    with pytest.raises(TypeError):
        UsageEvent("a", 1)
    with pytest.raises(ValueError):
        UsageEvent(tenant="", tokens=1)
    with pytest.raises(ValueError):
        UsageEvent(tenant="a", tokens=-1)
    assert UsageEvent(tenant="a", tokens=0).tokens == 0


def test_summary_defaults_are_empty_and_not_shared():
    a, b = Summary(), Summary()
    assert a.tokens_by_tenant == {} and a.errors == ()
    assert a.tokens_by_tenant is not b.tokens_by_tenant, "use default_factory for the dict"
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.errors = ()
    assert not hasattr(a, "__dict__"), "Summary must use __slots__"


def test_strict_raises_exception_group_after_processing_everything():
    raw = [{"tenant": "a"}, {"tenant": "b", "tokens": 1}, {"tenant": "b", "tokens": "x"}, {"tokens": 3}]
    with pytest.raises(ExceptionGroup) as eg:
        summarize(raw, strict=True)
    assert eg.value.message == "3 invalid events"
    assert len(eg.value.exceptions) == 3, "all failures are reported together"
    assert all(isinstance(e, InvalidEvent) for e in eg.value.exceptions)
    assert [e.index for e in eg.value.exceptions] == [0, 2, 3]


def test_strict_ok_when_clean_and_non_strict_never_raises():
    assert summarize(GOOD, strict=True).tokens_by_tenant["acme"] == 15
    assert len(summarize([{"x": 1}], strict=False).errors) == 1


def test_accepts_one_shot_generator_input():
    def gen():
        yield from GOOD
        yield {"tenant": "z"}

    s = summarize(gen())
    assert s.tokens_by_tenant["globex"] == 7
    assert [e.index for e in s.errors] == [3], "indices count positions in the generator"

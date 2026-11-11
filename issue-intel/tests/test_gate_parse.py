"""Gate output parsing tests (pure)."""
from __future__ import annotations

from app.agents.gate import parse_dotnet_test

GREEN = """
Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12
"""

RED = """
Failed Bug01TrailerTests.TrailerValueKeepsInnerColons [1 ms]
  Message: Assert.Equal() Failure
Failed!  - Failed:     1, Passed:    11, Skipped:     0, Total:    12
"""


def test_green_parse() -> None:
    result = parse_dotnet_test(GREEN)
    assert result.ok
    assert result.passed == 12
    assert result.failed == 0
    assert result.failing == []


def test_red_parse() -> None:
    result = parse_dotnet_test(RED)
    assert not result.ok
    assert result.passed == 11
    assert result.failed == 1
    assert [f.name for f in result.failing] == [
        "Bug01TrailerTests.TrailerValueKeepsInnerColons"
    ]


def test_unparseable_is_not_ok() -> None:
    assert not parse_dotnet_test("garbage output").ok

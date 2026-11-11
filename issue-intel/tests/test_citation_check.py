"""Citation check tests (pure)."""
from __future__ import annotations

from app.search.citations import check_citations


def test_citations_ok_when_all_retrieved() -> None:
    report = check_citations("Seen before [E1] and fixed [E2].", ["E1", "E2"])
    assert report.ok
    assert report.unknown == []


def test_citations_reject_unknown_id() -> None:
    report = check_citations("Seen before [E1] and [E9].", ["E1", "E2"])
    assert not report.ok
    assert report.unknown == ["E9"]


def test_no_citations_is_ok() -> None:
    assert check_citations("No evidence found.", ["E1"]).ok

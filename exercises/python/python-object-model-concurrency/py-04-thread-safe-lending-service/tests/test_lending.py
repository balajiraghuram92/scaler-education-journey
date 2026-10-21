import dataclasses
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pytest

from lending import (
    BorrowLimitReached,
    LendingService,
    LibraryError,
    Loan,
    NoCopiesAvailable,
    NotBorrowedByMember,
    UnknownItem,
)

NOW = datetime(2026, 1, 1, 9, 0)


def svc(copies=None, **kw):
    return LendingService(copies or {"N-1": 1, "N-2": 2}, clock=lambda: NOW, **kw)


def test_lend_returns_a_frozen_loan_due_14_days_from_the_injected_clock():
    loan = svc().lend("m1", "N-1")
    assert isinstance(loan, Loan)
    assert (loan.member_id, loan.isbn) == ("m1", "N-1")
    assert loan.due == NOW + timedelta(days=14), "due date = clock() + 14 days"
    assert loan.due == datetime(2026, 1, 15, 9, 0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        loan.isbn = "other"


def test_unknown_and_exhausted_items():
    s = svc()
    with pytest.raises(UnknownItem):
        s.lend("m1", "X")
    s.lend("m1", "N-1")
    with pytest.raises(NoCopiesAvailable):
        s.lend("m2", "N-1")


def test_borrow_limit():
    s = svc({"A": 5, "B": 5}, max_loans=2)
    s.lend("m1", "A")
    s.lend("m1", "B")
    with pytest.raises(BorrowLimitReached):
        s.lend("m1", "A")
    s.lend("m2", "A")  # the limit is per member


def test_checks_run_in_the_documented_order():
    s = svc({"A": 2, "B": 0}, max_loans=1)
    s.lend("m1", "A")
    with pytest.raises(UnknownItem):
        s.lend("m1", "nope")  # unknown ISBN wins over the member limit
    with pytest.raises(NoCopiesAvailable):
        s.lend("m1", "B")  # no copies wins over the member limit
    with pytest.raises(BorrowLimitReached):
        s.lend("m1", "A")  # a copy is left, but m1 is at the limit


def test_failed_lend_changes_nothing():
    s = svc({"A": 5, "B": 0}, max_loans=1)
    s.lend("m1", "A")
    for member, isbn, error in (("m1", "A", BorrowLimitReached), ("m2", "B", NoCopiesAvailable), ("m2", "Z", UnknownItem)):
        with pytest.raises(error):
            s.lend(member, isbn)
    assert s.available("A") == 4 and s.available("B") == 0
    assert len(s.active_loans("m1")) == 1 and s.active_loans("m2") == []


def test_return_restores_copy_and_rejects_strangers():
    s = svc()
    s.lend("m1", "N-1")
    with pytest.raises(NotBorrowedByMember):
        s.return_book("m2", "N-1")
    with pytest.raises(NotBorrowedByMember):
        s.return_book("m1", "N-2")
    assert s.available("N-1") == 0, "a rejected return must not give a copy back"
    s.return_book("m1", "N-1")
    assert s.available("N-1") == 1 and s.active_loans("m1") == []
    with pytest.raises(NotBorrowedByMember):
        s.return_book("m1", "N-1")  # returning twice
    s.lend("m3", "N-1")  # the copy is lendable again


def test_all_errors_share_a_base_class():
    for exc in (UnknownItem, NoCopiesAvailable, BorrowLimitReached, NotBorrowedByMember):
        assert issubclass(exc, LibraryError), f"{exc.__name__} must extend LibraryError"
    with pytest.raises(LibraryError):
        svc().lend("m1", "nope")


def test_construction_validates_and_copies_its_input():
    with pytest.raises(ValueError):
        svc(max_loans=0)
    source = {"A": 1}
    s = LendingService(source, clock=lambda: NOW)
    source["A"] = 99
    source["B"] = 1
    assert s.available("A") == 1, "the input mapping must be copied, not shared"
    with pytest.raises(UnknownItem):
        s.lend("m1", "B")


def test_snapshots_are_independent_copies():
    s = svc({"A": 3})
    s.lend("m1", "A")
    snapshot = s.active_loans("m1")
    snapshot.clear()
    assert len(s.active_loans("m1")) == 1, "active_loans must return a new list each time"
    assert s.active_loans("nobody") == []


def test_concurrent_lending_never_oversells():
    # The clock runs between the availability check and the update, so a missing lock
    # lets many threads pass the check. A short sleep widens that window deterministically.
    def slow_clock():
        time.sleep(0.002)
        return NOW

    s = LendingService({"N-1": 3}, max_loans=100, clock=slow_clock)

    def attempt(i):
        try:
            s.lend(f"m{i}", "N-1")
            return True
        except NoCopiesAvailable:
            return False

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(attempt, range(60)))
    assert sum(results) == 3, f"exactly 3 of 60 concurrent lends may succeed, got {sum(results)}"
    assert s.available("N-1") == 0, "the available count must not go negative or drift"

    limited = LendingService({"N-1": 100}, max_loans=2, clock=slow_clock)

    def same_member(_):
        try:
            limited.lend("m1", "N-1")
            return True
        except BorrowLimitReached:
            return False

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(same_member, range(30)))
    assert sum(results) == 2, "one member must never exceed max_loans under concurrency"
    assert len(limited.active_loans("m1")) == 2 and limited.available("N-1") == 98

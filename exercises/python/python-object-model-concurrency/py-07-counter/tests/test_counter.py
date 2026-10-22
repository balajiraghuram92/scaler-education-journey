import sys
import threading
import time

import pytest

from config.counter import Counter, concurrent_dec, concurrent_inc


def run_threads(targets, timeout=20):
    threads = [threading.Thread(target=t, daemon=True) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "threads did not finish in time (deadlock?)"


@pytest.fixture
def tiny_switch_interval():
    """Force the interpreter to switch threads very often, to expose lost updates."""
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    yield
    sys.setswitchinterval(old)


def test_initial_value_and_single_thread_updates():
    c = Counter(5)
    assert c.getValue() == 5, "getValue should return the initial count"
    c.incValue(3)
    assert c.getValue() == 8, "incValue(3) should add 3"
    c.decValue(10)
    assert c.getValue() == -2, "decValue(10) should subtract 10 and may go negative"


def test_helpers_call_the_matching_method_1000_times():
    class Spy:
        def __init__(self):
            self.inc_calls = []
            self.dec_calls = []

        def incValue(self, offset):
            self.inc_calls.append(offset)

        def decValue(self, offset):
            self.dec_calls.append(offset)

    spy = Spy()
    concurrent_inc(spy, 3)
    assert spy.inc_calls == [3] * 1000, "concurrent_inc must call incValue(offset) exactly 1000 times"
    assert spy.dec_calls == [], "concurrent_inc must not touch decValue"
    concurrent_dec(spy, 2)
    assert spy.dec_calls == [2] * 1000, "concurrent_dec must call decValue(offset) exactly 1000 times"


def test_balanced_threads_return_to_initial_value(tiny_switch_interval):
    counter = Counter(0)
    targets = []
    for _ in range(10):
        targets.append(lambda: concurrent_inc(counter, 1))
        targets.append(lambda: concurrent_dec(counter, 1))
    run_threads(targets)
    assert counter.getValue() == 0, "10 x 1000 increments and 10 x 1000 decrements must cancel out exactly"


def test_unbalanced_offsets_give_exact_arithmetic_result(tiny_switch_interval):
    counter = Counter(5)
    targets = []
    for _ in range(10):
        targets.append(lambda: concurrent_inc(counter, 2))
        targets.append(lambda: concurrent_dec(counter, 1))
    run_threads(targets)
    assert counter.getValue() == 5 + 10 * 1000 * 2 - 10 * 1000, "expected 10005 after the mixed updates"


class SlowInt(int):
    """An int whose arithmetic pauses mid-update, so an unprotected read-modify-write loses updates."""

    def __radd__(self, other):
        threading.Event().wait(0.0005)
        return int.__radd__(self, other)

    def __rsub__(self, other):
        threading.Event().wait(0.0005)
        return int.__rsub__(self, other)


def test_no_lost_updates_when_updates_are_slow():
    counter = Counter(0)

    def incrementer():
        for _ in range(20):
            counter.incValue(SlowInt(1))

    def decrementer():
        for _ in range(15):
            counter.decValue(SlowInt(1))

    run_threads([incrementer] * 4 + [decrementer] * 4)
    assert counter.getValue() == 4 * 20 - 4 * 15, (
        "updates were lost: the read-modify-write in incValue/decValue must run entirely under the lock"
    )


def test_does_not_use_sleep_to_wait(monkeypatch):
    def forbidden(_seconds):
        raise AssertionError("time.sleep must not be used")

    monkeypatch.setattr(time, "sleep", forbidden)
    counter = Counter(0)
    run_threads([lambda: concurrent_inc(counter, 1), lambda: concurrent_dec(counter, 1)])
    assert counter.getValue() == 0

import math
import threading
import time

import pytest

from config.factorial import FactorialThread, compute_large_factorial


def test_thread_initial_state():
    t = FactorialThread(5)
    assert isinstance(t, threading.Thread), "FactorialThread must extend threading.Thread"
    assert t.n == 5
    assert t.result is None, "result starts as None until the thread has run"
    assert not t.is_alive()


def test_result_is_available_after_join():
    t = FactorialThread(6)
    t.start()
    t.join(timeout=5)
    assert t.result == 720, "run() must store math.factorial(n) in self.result"


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (5, 120), (10, 3628800)])
def test_small_values(n, expected):
    assert compute_large_factorial(n) == expected


def test_large_value_is_an_exact_int():
    result = compute_large_factorial(1000)
    assert isinstance(result, int)
    assert result == math.factorial(1000), "no precision may be lost for large inputs"


def test_computation_runs_on_a_worker_thread(monkeypatch):
    seen = []
    real = math.factorial

    def spy(n):
        seen.append(threading.current_thread())
        return real(n)

    monkeypatch.setattr(math, "factorial", spy)
    assert compute_large_factorial(4) == 24
    assert len(seen) == 1 and seen[0] is not threading.main_thread(), "math.factorial must be called inside the worker thread"
    assert isinstance(seen[0], FactorialThread)


def test_compute_waits_for_a_slow_worker(monkeypatch):
    real = math.factorial

    def slow(n):
        time.sleep(0.05)
        return real(n)

    monkeypatch.setattr(math, "factorial", slow)
    assert compute_large_factorial(7) == 5040, "without join() the result would still be None"


def test_each_call_uses_a_fresh_finished_thread():
    baseline = threading.active_count()
    assert [compute_large_factorial(n) for n in (3, 4, 5)] == [6, 24, 120]
    assert threading.active_count() == baseline, "threads must be joined, not left running"


def test_independent_threads_keep_independent_results():
    a, b = FactorialThread(5), FactorialThread(6)
    a.start()
    b.start()
    a.join(timeout=5)
    b.join(timeout=5)
    assert (a.result, b.result) == (120, 720)

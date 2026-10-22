import queue
import sys
import threading

import pytest

from tmap import SafeCounter, threaded_map

WAIT = 5  # generous upper bound for events/barriers; never reached by a correct implementation


def test_results_keep_input_order_even_when_finish_order_differs():
    # Item 0 cannot finish until item 3 has finished, so completion order is forced to differ.
    last_done = threading.Event()

    def fn(i: int) -> int:
        if i == 0:
            assert last_done.wait(WAIT), "item 3 never finished: workers are not running in parallel"
        if i == 3:
            last_done.set()
        return i * i

    assert threaded_map(fn, [0, 1, 2, 3], workers=4) == [0, 1, 4, 9], "results must follow input order"


def test_basic_mapping_and_input_types():
    assert threaded_map(lambda x: x * x, [1, 2, 3, 4], workers=2) == [1, 4, 9, 16]
    assert threaded_map(str, (1, 2, 3)) == ["1", "2", "3"], "tuples are sequences too"
    assert threaded_map(lambda x: None, range(3)) == [None, None, None], "None results are kept"
    assert threaded_map(lambda x: x + 1, [1, 2, 3], workers=1) == [2, 3, 4], "a single worker still works"


def test_empty_input_and_invalid_workers(monkeypatch):
    def no_threads(self):
        raise AssertionError("no thread may be started for empty input")

    monkeypatch.setattr(threading.Thread, "start", no_threads)
    assert threaded_map(str, []) == []
    monkeypatch.undo()
    for bad in (0, -2):
        with pytest.raises(ValueError):
            threaded_map(str, [1], workers=bad)


def test_runs_items_in_parallel_up_to_the_worker_count():
    # Three items wait for each other: this only completes if three threads run at the same time.
    barrier = threading.Barrier(3, timeout=WAIT)

    def meet(i: int) -> int:
        barrier.wait()
        return i

    assert threaded_map(meet, [0, 1, 2], workers=3) == [0, 1, 2]


def test_thread_count_is_bounded_by_workers_and_by_items():
    idents: set[int] = set()
    lock = threading.Lock()

    def record(_: int) -> None:
        with lock:
            idents.add(threading.get_ident())

    threaded_map(record, list(range(50)), workers=3)
    assert 1 <= len(idents) <= 3, f"at most 3 threads may be used, saw {len(idents)}"
    idents.clear()
    threaded_map(record, [1, 2], workers=10)
    assert len(idents) <= 2, "never more threads than items"
    assert threading.main_thread().ident not in idents, "work must run in worker threads"


def test_active_workers_never_exceed_limit_and_no_threads_leak():
    baseline = threading.active_count()
    active, peak, lock = 0, 0, threading.Lock()

    def tracked(_: int) -> None:
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        with lock:
            active -= 1

    threaded_map(tracked, list(range(40)), workers=4)
    assert peak <= 4, f"peak concurrency {peak} exceeded workers=4"
    assert threading.active_count() == baseline, "all worker threads must be joined before returning"


def test_waits_for_everything_then_raises_group_in_input_order():
    done = SafeCounter()

    def maybe_fail(i: int) -> int:
        done.incr()
        if i % 2:
            raise ValueError(f"bad {i}")
        return i

    baseline = threading.active_count()
    with pytest.raises(ExceptionGroup) as info:
        threaded_map(maybe_fail, list(range(6)), workers=3)
    group = info.value
    assert done.value == 6, "no task may be abandoned after a failure"
    assert group.message == "threaded_map failed"
    assert [str(e) for e in group.exceptions] == ["bad 1", "bad 3", "bad 5"], "exceptions are ordered by input index"
    assert all(isinstance(e, ValueError) for e in group.exceptions)
    assert threading.active_count() == baseline, "threads must be joined before the group is raised"


def test_work_is_distributed_through_a_queue(monkeypatch):
    created = []
    real_queue = queue.Queue

    class Spy(real_queue):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)

    monkeypatch.setattr(queue, "Queue", Spy)
    assert threaded_map(lambda x: x, [1, 2, 3], workers=2) == [1, 2, 3]
    assert created, "use queue.Queue to hand out work to the workers"


def test_safe_counter_semantics():
    c = SafeCounter()
    assert c.value == 0
    assert c.incr() == 1 and c.incr(5) == 6, "incr returns the new value"
    assert c.incr(-2) == 4 and c.value == 4
    assert SafeCounter(10).value == 10


def test_safe_counter_has_no_lost_updates():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # switch threads very often to expose unprotected read-modify-write
    try:
        c = SafeCounter()

        def bump(_: int) -> None:
            for _ in range(5_000):
                c.incr()

        threaded_map(bump, list(range(8)), workers=8)
        assert c.value == 40_000, f"lost updates: expected 40000, got {c.value}"
    finally:
        sys.setswitchinterval(old)

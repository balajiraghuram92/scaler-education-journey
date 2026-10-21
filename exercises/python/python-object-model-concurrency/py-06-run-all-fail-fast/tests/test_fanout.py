import dataclasses
import threading

import pytest

from fanout import Outcome, run_all


def test_preserves_input_order_even_when_finish_order_differs():
    done = [threading.Event() for _ in range(3)]

    def fn(x: int) -> int:
        if x < 2:
            assert done[x + 1].wait(2), "task should be released by the later task finishing first"
        done[x].set()
        return x * 10

    out = run_all(fn, [0, 1, 2], max_workers=3)
    assert [o.value for o in out] == [0, 10, 20], "results must follow input order, not completion order"
    assert [o.index for o in out] == [0, 1, 2], "each Outcome.index must be its input position"
    assert all(o.ok for o in out)


def test_errors_are_captured_not_raised():
    def fn(x: int) -> int:
        if x == 1:
            raise ValueError("bad")
        return x

    out = run_all(fn, [0, 1, 2])
    assert [o.ok for o in out] == [True, False, True], "only the failing item should be not ok"
    assert isinstance(out[1].error, ValueError) and str(out[1].error) == "bad"
    assert out[1].value is None and out[1].cancelled is False
    assert [out[0].value, out[2].value] == [0, 2], "other items still run when fail_fast is off"


def test_without_fail_fast_every_item_runs():
    started = []
    lock = threading.Lock()

    def fn(x: int) -> int:
        with lock:
            started.append(x)
        raise RuntimeError(f"fail {x}")

    out = run_all(fn, range(8), max_workers=2)
    assert sorted(started) == list(range(8)), "fail_fast=False must not cancel anything"
    assert all(o.error is not None and not o.cancelled for o in out)


def test_fail_fast_cancels_queued_work_but_lets_running_tasks_finish():
    first_running = threading.Event()
    gate = threading.Event()
    started = []
    lock = threading.Lock()
    release = threading.Timer(0.15, gate.set)  # frees the blocked tasks once the queue was cancelled

    def fn(x: int) -> int:
        with lock:
            started.append(x)
        if x == 0:
            first_running.set()
            gate.wait(2)
            return 100
        if x == 1:
            assert first_running.wait(2)
            release.start()
            raise RuntimeError("boom")
        gate.wait(2)
        return x

    try:
        out = run_all(fn, [0, 1, 2, 3, 4, 5], max_workers=2, fail_fast=True)
    finally:
        release.cancel()
        gate.set()
    assert len(out) == 6
    assert isinstance(out[1].error, RuntimeError), "the failing task reports its error"
    assert out[0].ok and out[0].value == 100, "an already-running task must finish normally"
    for i in (3, 4, 5):
        assert out[i].cancelled, f"item {i} was still queued and must be cancelled"
        assert out[i].value is None and out[i].error is None and not out[i].ok
        assert i not in started, f"item {i} must never start"


def test_rejects_bad_worker_count():
    with pytest.raises(ValueError):
        run_all(str, [1], max_workers=0)
    with pytest.raises(ValueError):
        run_all(str, [1], max_workers=-3)


def test_empty_and_generator_input():
    assert run_all(str, [], fail_fast=True) == []
    assert run_all(str, [], fail_fast=False) == []
    out = run_all(lambda x: x + 1, (i for i in range(3)))
    assert [o.value for o in out] == [1, 2, 3], "any iterable, including a one-shot generator, is accepted"


def test_respects_max_workers_and_runs_in_parallel():
    barrier = threading.Barrier(2)
    lock = threading.Lock()
    active = 0
    peak = 0

    def fn(x: int) -> int:
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        barrier.wait(timeout=2)  # needs two tasks in flight at once
        with lock:
            active -= 1
        return x

    out = run_all(fn, range(4), max_workers=2)
    assert all(o.ok for o in out)
    assert peak == 2, f"expected exactly 2 concurrent tasks with max_workers=2, saw {peak}"


def test_outcome_is_frozen_slotted_dataclass_with_ok_property():
    assert dataclasses.is_dataclass(Outcome)
    o = Outcome(0)
    assert (o.index, o.value, o.error, o.cancelled) == (0, None, None, False), "defaults"
    assert o.ok is True
    assert Outcome(1, value=5).ok is True
    assert Outcome(1, error=ValueError("x")).ok is False
    assert Outcome(1, cancelled=True).ok is False
    with pytest.raises(dataclasses.FrozenInstanceError):
        o.index = 9
    assert not hasattr(o, "__dict__"), "Outcome must use __slots__"
    with pytest.raises(AttributeError):
        o.ok = False

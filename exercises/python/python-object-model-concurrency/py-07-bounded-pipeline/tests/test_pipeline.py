import dataclasses
import queue
import threading

import pytest

from pipeline import Pipeline, PipelineClosed, Result


def run_in_thread(fn):
    box = {}

    def target():
        try:
            box["value"] = fn()
        except BaseException as exc:  # noqa: BLE001 - reported to the test
            box["error"] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t, box


def test_results_in_submission_order():
    p = Pipeline(lambda x: x * 2, workers=4, max_pending=2)
    for i in range(20):
        p.submit(i)
    out = p.close()
    assert [r.value for r in out] == [i * 2 for i in range(20)], "results must be sorted by submission order"
    assert [r.seq for r in out] == list(range(20))


def test_errors_captured_per_item_and_pipeline_keeps_going():
    def fn(x: int) -> int:
        if x == 3:
            raise ValueError("bad")
        return x

    p = Pipeline(fn, workers=2)
    for i in range(10):
        p.submit(i)
    out = p.close()
    assert len(out) == 10, "one failure must not stop the other items"
    assert isinstance(out[3].error, ValueError) and out[3].value is None
    assert [r.value for r in out if r.error is None] == [0, 1, 2, 4, 5, 6, 7, 8, 9]


def test_submit_returns_sequence_numbers():
    p = Pipeline(str, workers=2)
    assert [p.submit(x) for x in "abc"] == [0, 1, 2]
    p.close()


def test_backpressure_times_out_when_full_and_does_not_consume_a_sequence_number():
    gate, started = threading.Event(), threading.Event()

    def fn(x: int) -> int:
        started.set()
        gate.wait(5)
        return x

    p = Pipeline(fn, workers=1, max_pending=1)
    assert p.submit(1) == 0
    assert started.wait(2), "the worker should have picked up the first item"
    assert p.submit(2) == 1  # fills the queue
    with pytest.raises(queue.Full):
        p.submit(3, timeout=0.05)
    gate.set()
    assert p.submit(4) == 2, "a submit that timed out must not use up a sequence number"
    assert [r.value for r in p.close()] == [1, 2, 4]


def test_submit_blocks_while_queue_is_full_until_space_frees():
    gate, started = threading.Event(), threading.Event()

    def fn(x: int) -> int:
        started.set()
        gate.wait(5)
        return x

    p = Pipeline(fn, workers=1, max_pending=1)
    p.submit(1)
    assert started.wait(2)
    p.submit(2)
    t, box = run_in_thread(lambda: p.submit(3))
    t.join(0.1)
    assert t.is_alive(), "submit must block while the queue is full"
    gate.set()
    t.join(5)
    assert not t.is_alive() and box.get("value") == 2, "the blocked submit should complete with seq 2"
    assert [r.value for r in p.close()] == [1, 2, 3]


def test_close_waits_for_queued_items_and_returns_all_results():
    gate = threading.Event()

    def fn(x: int) -> int:
        gate.wait(5)
        return x

    p = Pipeline(fn, workers=2, max_pending=8)
    for i in range(5):
        p.submit(i)
    t, box = run_in_thread(p.close)
    t.join(0.1)
    assert t.is_alive(), "close() must wait for queued and running items to finish"
    gate.set()
    t.join(5)
    assert not t.is_alive(), "close() never returned"
    assert [r.value for r in box["value"]] == [0, 1, 2, 3, 4]


def test_submit_after_close_raises_and_close_is_idempotent():
    p = Pipeline(str, workers=1)
    p.submit(1)
    first = p.close()
    assert p.close() == first, "a second close() returns the same results"
    assert issubclass(PipelineClosed, RuntimeError)
    with pytest.raises(PipelineClosed):
        p.submit(2)


def test_close_stops_and_joins_the_worker_threads():
    before = set(threading.enumerate())
    p = Pipeline(str, workers=3)
    spawned = set(threading.enumerate()) - before
    assert spawned, "the pipeline should start its worker threads in the constructor"
    p.submit(1)
    p.close()
    assert not any(t.is_alive() for t in spawned), "close() must stop and join every worker"


def test_concurrent_submitters_lose_nothing_and_get_unique_ordered_sequence_numbers():
    p = Pipeline(lambda x: x, workers=3, max_pending=4)
    seq_of = {}
    lock = threading.Lock()

    def producer(base: int) -> None:
        for i in range(100):
            seq = p.submit((base, i))
            with lock:
                seq_of[(base, i)] = seq

    bases = (0, 1000, 2000, 3000)
    threads = [threading.Thread(target=producer, args=(b,), daemon=True) for b in bases]
    for t in threads:
        t.start()
    for t in threads:
        t.join(20)
    assert not any(t.is_alive() for t in threads), "producers did not finish"
    out = p.close()
    assert len(out) == 400
    assert sorted(seq_of.values()) == list(range(400)), "sequence numbers must be unique and gap-free"
    for item, seq in seq_of.items():
        assert out[seq].seq == seq and out[seq].value == item, f"result {seq} does not belong to item {item}"
    for b in bases:
        seqs = [seq_of[(b, i)] for i in range(100)]
        assert seqs == sorted(seqs), "one producer's items must keep their relative order"


def test_submit_racing_with_close_never_loses_an_accepted_item():
    p = Pipeline(lambda x: x, workers=2, max_pending=2)
    accepted = []
    lock = threading.Lock()
    warm = threading.Event()

    def producer(base: int) -> None:
        i = 0
        while True:
            try:
                seq = p.submit((base, i))
            except PipelineClosed:
                return
            with lock:
                accepted.append(seq)
                if len(accepted) >= 30:
                    warm.set()
            i += 1

    threads = [threading.Thread(target=producer, args=(b,), daemon=True) for b in range(4)]
    for t in threads:
        t.start()
    assert warm.wait(10), "producers never got going"
    out = p.close()
    for t in threads:
        t.join(10)
    assert not any(t.is_alive() for t in threads), "producers must see PipelineClosed and stop"
    assert [r.seq for r in out] == sorted(accepted), "every accepted submit needs a result, and nothing else"
    assert [r.seq for r in out] == list(range(len(out)))


def test_invalid_arguments():
    with pytest.raises(ValueError):
        Pipeline(str, workers=0)
    with pytest.raises(ValueError):
        Pipeline(str, max_pending=0)


def test_result_is_frozen_slotted_dataclass():
    assert dataclasses.is_dataclass(Result)
    r = Result(1)
    assert (r.seq, r.value, r.error) == (1, None, None), "value and error default to None"
    assert Result(2, value="x").value == "x"
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.seq = 5
    assert not hasattr(r, "__dict__"), "Result must use __slots__"

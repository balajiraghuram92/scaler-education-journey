import threading
from collections import Counter

import pytest

from config import tableCreator as module
from config.tableCreator import Client, TableCreator


def expected_table(num):
    return [f"{num} times {i} is {num * i}" for i in range(1, 11)]


@pytest.fixture
def printed(monkeypatch):
    """Capture each print() call atomically, so concurrent threads cannot split a line."""
    lines = []

    def fake_print(*args, sep=" ", **kwargs):
        lines.append(sep.join(str(a) for a in args))

    monkeypatch.setattr(module, "print", fake_print, raising=False)
    return lines


def run_client(monkeypatch, n):
    monkeypatch.setattr("builtins.input", lambda prompt="": str(n))
    Client.main()


def test_table_creator_is_a_thread_that_stores_its_number():
    t = TableCreator(3)
    assert isinstance(t, threading.Thread), "TableCreator must extend threading.Thread"
    assert t.num == 3
    assert not t.is_alive()


def test_run_prints_ten_lines_in_the_exact_format(capsys):
    TableCreator(3).run()
    out = capsys.readouterr().out
    assert out.splitlines() == expected_table(3)
    assert out.endswith("\n") and "3 times 4 is 12" in out


@pytest.mark.parametrize("num", [0, -3, 12])
def test_zero_negative_and_larger_numbers(capsys, num):
    TableCreator(num).run()
    assert capsys.readouterr().out.splitlines() == expected_table(num)


def test_started_thread_prints_its_whole_table(printed):
    t = TableCreator(7)
    t.start()
    t.join(timeout=5)
    assert printed == expected_table(7), "one print call per line, in order, from inside the thread"


def test_client_prints_every_table_completely_and_correctly(monkeypatch, printed):
    run_client(monkeypatch, 4)
    expected = [line for n in range(1, 5) for line in expected_table(n)]
    assert len(printed) == 40, f"4 tables of 10 lines expected, got {len(printed)}"
    assert Counter(printed) == Counter(expected), "every line of every table must appear exactly once (order may vary)"


def test_lines_of_one_table_keep_their_own_order(monkeypatch, printed):
    run_client(monkeypatch, 3)
    for n in (1, 2, 3):
        mine = [line for line in printed if line.startswith(f"{n} times ")]
        assert mine == expected_table(n), f"table {n} must be printed in order by its own thread"


def test_client_starts_all_threads_before_joining_any(monkeypatch, printed):
    # Each thread waits at a barrier first. If the client joins thread 1 before starting thread 2,
    # the barrier can never fill and breaks after the timeout.
    barrier = threading.Barrier(3, timeout=3)
    outcome = []
    original_run = TableCreator.run

    def meet_then_run(self):
        try:
            barrier.wait()
            outcome.append("met")
        except threading.BrokenBarrierError:
            outcome.append("broken")
        original_run(self)

    monkeypatch.setattr(TableCreator, "run", meet_then_run)
    run_client(monkeypatch, 3)
    assert outcome == ["met"] * 3, "start every thread first, then join them all"


def test_client_waits_for_all_threads_and_handles_zero(monkeypatch, printed):
    baseline = threading.active_count()
    run_client(monkeypatch, 2)
    assert threading.active_count() == baseline and len(printed) == 20, "main must join every thread before returning"
    printed.clear()
    run_client(monkeypatch, 0)
    assert printed == [], "no tables for n = 0"

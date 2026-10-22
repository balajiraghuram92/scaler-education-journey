import threading

from config import threads as threads_module
from config.threads import Adder, Client, Subtractor

MAIN = "I am the main class"
ADDER = "I am the Adder class"
SUB = "I am the Subtractor class"


def test_threads_are_thread_subclasses_that_print_their_line(capsys):
    assert issubclass(Adder, threading.Thread) and issubclass(Subtractor, threading.Thread)
    Adder().run()
    Subtractor().run()
    assert capsys.readouterr().out.splitlines() == [ADDER, SUB], "run() prints one fixed line per class"


def test_main_prints_three_lines_and_the_main_line_is_first(capsys):
    Client.main()
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 3, f"expected exactly 3 lines, got {lines}"
    assert lines[0] == MAIN, "the main line must print before any thread starts"


def test_both_thread_lines_appear_in_either_order(capsys):
    Client.main()
    lines = capsys.readouterr().out.splitlines()
    assert sorted(lines[1:]) == sorted([ADDER, SUB]), "both thread lines must appear once; their order is up to the scheduler"


def test_main_joins_both_threads_before_returning(capsys):
    baseline = threading.active_count()
    Client.main()
    assert threading.active_count() == baseline, "main must join both threads before it returns"
    assert len(capsys.readouterr().out.splitlines()) == 3, "all output must exist once main has returned"


def test_both_threads_are_started_before_either_is_joined(monkeypatch):
    # Each thread waits for the other at a barrier. If main joins the first thread before starting
    # the second, the barrier can never fill and breaks after the timeout.
    barrier = threading.Barrier(2, timeout=3)
    outcome = []

    def meet(self):
        try:
            barrier.wait()
            outcome.append("met")
        except threading.BrokenBarrierError:
            outcome.append("broken")

    monkeypatch.setattr(threads_module.Adder, "run", meet)
    monkeypatch.setattr(threads_module.Subtractor, "run", meet)
    Client.main()
    assert outcome == ["met", "met"], "start both threads first, then join both (joining early serialises them)"


def test_each_class_runs_on_its_own_worker_thread(monkeypatch):
    seen = []
    monkeypatch.setattr(threads_module.Adder, "run", lambda self: seen.append(threading.current_thread()))
    monkeypatch.setattr(threads_module.Subtractor, "run", lambda self: seen.append(threading.current_thread()))
    Client.main()
    assert len(seen) == 2 and len(set(seen)) == 2, "two different threads must run the two classes"
    assert threading.main_thread() not in seen, "the work must not run on the main thread"


def test_main_can_be_called_repeatedly(capsys):
    Client.main()
    Client.main()
    lines = capsys.readouterr().out.splitlines()
    assert lines.count(MAIN) == 2 and lines.count(ADDER) == 2 and lines.count(SUB) == 2


def test_main_is_a_static_method():
    assert isinstance(Client.__dict__["main"], staticmethod)

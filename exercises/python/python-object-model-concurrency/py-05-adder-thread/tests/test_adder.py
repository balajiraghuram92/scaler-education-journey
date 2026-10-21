import threading

import pytest

from config import adder as adder_module
from config.adder import Adder, Client


def feed_input(monkeypatch, *answers):
    """Replace input() with scripted answers and record the prompts."""
    prompts = []
    it = iter(answers)

    def fake_input(prompt=""):
        prompts.append(prompt)
        return next(it)

    monkeypatch.setattr("builtins.input", fake_input)
    return prompts


def test_adder_is_a_thread_that_stores_its_numbers():
    a = Adder(2, 3)
    assert isinstance(a, threading.Thread), "Adder must extend threading.Thread"
    assert (a.num1, a.num2) == (2, 3)
    assert not a.is_alive(), "constructing the thread must not start it"


def test_started_adder_prints_the_sum(capsys):
    a = Adder(5, 7)
    a.start()
    a.join(timeout=5)
    assert capsys.readouterr().out == "12\n", "run() must print just the sum and a newline"


def test_work_happens_on_the_worker_thread(monkeypatch):
    seen = []
    monkeypatch.setattr(adder_module, "print", lambda *a, **k: seen.append(threading.current_thread()), raising=False)
    a = Adder(1, 1)
    a.start()
    a.join(timeout=5)
    assert len(seen) == 1 and seen[0] is a, "the sum must be printed from inside the Adder thread (start(), not run())"


@pytest.mark.parametrize("x, y, expected", [(0, 0, "0"), (-3, 5, "2"), (-4, -6, "-10"), (10**12, 1, str(10**12 + 1))])
def test_sums_of_zero_negative_and_large_numbers(capsys, x, y, expected):
    a = Adder(x, y)
    a.start()
    a.join(timeout=5)
    assert capsys.readouterr().out == expected + "\n"


def test_client_reads_two_numbers_with_the_documented_prompts(monkeypatch, capsys):
    prompts = feed_input(monkeypatch, "5", "7")
    Client.main()
    assert prompts == ["Enter the first number: ", "Enter the second number: "], "prompts must match exactly and be asked in order"
    assert capsys.readouterr().out == "12\n"


def test_client_converts_input_to_integers(monkeypatch, capsys):
    feed_input(monkeypatch, "10", "20")
    Client.main()
    assert capsys.readouterr().out == "30\n", "'10' + '20' would be '1020': convert with int()"


def test_client_waits_for_the_thread_before_returning(monkeypatch, capsys):
    baseline = threading.active_count()
    feed_input(monkeypatch, "1", "2")
    Client.main()
    assert threading.active_count() == baseline, "main must join() the Adder thread before it returns"
    assert capsys.readouterr().out == "3\n", "the output must already be there when main returns"


def test_client_main_is_a_static_method():
    assert isinstance(Client.__dict__["main"], staticmethod), "Client.main must be a @staticmethod"

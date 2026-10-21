import itertools
import sys
import threading

import pytest

from config.zeroEvenOdd import PrintNumber, ZeroEvenOdd


class Recorder:
    """Stand-in for PrintNumber that records what was accepted, in order."""

    def __init__(self):
        self.values = []

    def accept(self, x):
        self.values.append(x)


def expected(n):
    out = []
    for i in range(1, n + 1):
        out += [0, i]
    return out


def run(n, order=("zero", "even", "odd"), printer=None, timeout=10):
    zeo = ZeroEvenOdd(n)
    printer = printer if printer is not None else Recorder()
    threads = [threading.Thread(target=getattr(zeo, name), args=(printer,), daemon=True) for name in order]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), f"deadlock: threads still running for n={n}, order={order}"
    return printer


def test_n_five_prints_0102030405():
    rec = run(5)
    assert rec.values == [0, 1, 0, 2, 0, 3, 0, 4, 0, 5], "expected 0102030405"


@pytest.mark.parametrize("order", list(itertools.permutations(("zero", "even", "odd"))))
def test_any_thread_start_order_gives_correct_output(order):
    rec = run(7, order=order)
    assert rec.values == expected(7), f"wrong output when threads start as {order}"


def test_n_one_has_no_even_work_and_does_not_deadlock():
    rec = run(1)
    assert rec.values == [0, 1], "n=1 must print 01"


def test_even_n_and_larger_values_under_heavy_switching():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        for n in (2, 50, 51):
            for order in (("odd", "even", "zero"), ("even", "zero", "odd")):
                assert run(n, order=order).values == expected(n), f"wrong output for n={n}, order={order}"
    finally:
        sys.setswitchinterval(old)


def test_output_goes_through_print_number_accept(capsys):
    run(8, printer=PrintNumber())
    assert capsys.readouterr().out == "0102030405060708", "use printNumber.accept(x) for every number, including zeros"


def test_print_number_helper_is_unchanged(capsys):
    PrintNumber().accept(3)
    PrintNumber().accept(0)
    assert capsys.readouterr().out == "30", "PrintNumber.accept must print the number with no newline"

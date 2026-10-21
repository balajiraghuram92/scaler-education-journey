import sys
import threading
import time

import pytest

from config.fooBar import FooBar


def run_pair(n, bar_first=False, timeout=10):
    fb = FooBar(n)
    foo_t = threading.Thread(target=fb.foo, daemon=True)
    bar_t = threading.Thread(target=fb.bar, daemon=True)
    pair = [bar_t, foo_t] if bar_first else [foo_t, bar_t]
    for t in pair:
        t.start()
    for t in pair:
        t.join(timeout)
    assert not any(t.is_alive() for t in pair), "threads did not finish (deadlock?)"


@pytest.mark.parametrize("bar_first", [False, True])
def test_output_is_foobar_repeated_n_times(capsys, bar_first):
    run_pair(5, bar_first=bar_first)
    assert capsys.readouterr().out == "foobar" * 5, "expected 'foobar' x 5 with no separators or newlines"


def test_n_zero_prints_nothing_and_does_not_hang(capsys):
    run_pair(0)
    assert capsys.readouterr().out == "", "n=0 must print nothing"


def test_n_one(capsys):
    run_pair(1, bar_first=True)
    assert capsys.readouterr().out == "foobar"


def test_strict_alternation_under_heavy_switching(capsys):
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        for bar_first in (True, False, True, False):
            run_pair(300, bar_first=bar_first)
    finally:
        sys.setswitchinterval(old)
    assert capsys.readouterr().out == "foobar" * 300 * 4, "prints must alternate foo, bar, foo, bar ..."


def test_bar_cannot_print_before_foo(capsys):
    fb = FooBar(1)
    bar_t = threading.Thread(target=fb.bar, daemon=True)
    bar_t.start()
    time.sleep(0.1)
    assert capsys.readouterr().out == "", "bar must wait until foo has printed"
    assert bar_t.is_alive(), "bar should be blocked waiting for foo"
    foo_t = threading.Thread(target=fb.foo, daemon=True)
    foo_t.start()
    foo_t.join(5)
    bar_t.join(5)
    assert not foo_t.is_alive() and not bar_t.is_alive()
    assert capsys.readouterr().out == "foobar"


def test_foo_cannot_run_ahead_of_bar(capsys):
    fb = FooBar(3)
    foo_t = threading.Thread(target=fb.foo, daemon=True)
    foo_t.start()
    time.sleep(0.1)
    assert capsys.readouterr().out == "foo", "with no bar thread, foo may print once and must then block"
    assert foo_t.is_alive(), "foo must wait for bar before its second iteration"
    bar_t = threading.Thread(target=fb.bar, daemon=True)
    bar_t.start()
    foo_t.join(5)
    bar_t.join(5)
    assert not foo_t.is_alive() and not bar_t.is_alive()
    assert capsys.readouterr().out == "barfoobarfoobar"

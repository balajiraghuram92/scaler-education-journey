import itertools
import threading
import time

import pytest

from config.printInOrder import Foo

NAMES = ("first", "second", "third")


def start(foo, name):
    t = threading.Thread(target=getattr(foo, name), daemon=True)
    t.start()
    return t


def join_all(threads, timeout=5):
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "a thread never finished (deadlock?)"


def test_output_starts_empty():
    assert Foo().output == [], "output must start as an empty list"


@pytest.mark.parametrize("order", list(itertools.permutations(NAMES)))
def test_runs_in_order_for_every_start_order(order):
    foo = Foo()
    threads = [start(foo, name) for name in order]
    join_all(threads)
    assert foo.output == ["first", "second", "third"], f"threads started as {order} must still output in order"


def test_second_and_third_block_until_first_has_run():
    foo = Foo()
    waiting = [start(foo, "third"), start(foo, "second")]
    time.sleep(0.1)
    assert foo.output == [], "second and third must not append before first() has run"
    assert all(t.is_alive() for t in waiting), "second and third should be blocked, not finished"
    join_all([start(foo, "first")] + waiting)
    assert foo.output == ["first", "second", "third"]


def test_third_waits_for_second_even_after_first_ran():
    foo = Foo()
    first = start(foo, "first")
    third = start(foo, "third")
    join_all([first])
    time.sleep(0.1)
    assert foo.output == ["first"], "third must wait for second, not just for first"
    assert third.is_alive(), "third should still be blocked"
    join_all([start(foo, "second"), third])
    assert foo.output == ["first", "second", "third"]


def test_independent_instances_do_not_share_state():
    a, b = Foo(), Foo()
    join_all([start(a, "first"), start(a, "second"), start(a, "third")])
    assert b.output == [], "b must be unaffected by a's calls"
    join_all([start(b, name) for name in reversed(NAMES)])
    assert b.output == ["first", "second", "third"]
    assert a.output == ["first", "second", "third"]

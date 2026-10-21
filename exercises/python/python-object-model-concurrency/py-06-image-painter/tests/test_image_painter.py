import threading
import time

import pytest

from config.imagePainter import divide_and_paint, paint_quadrant

COLORS = ["red", "blue", "green", "yellow"]


def blank(rows, cols):
    return [[0] * cols for _ in range(rows)]


def expected(rows, cols, colors=COLORS):
    mr, mc = rows // 2, cols // 2
    return [
        [colors[(0 if i < mr else 2) + (0 if j < mc else 1)] for j in range(cols)]
        for i in range(rows)
    ]


class HookRow(list):
    """A matrix row that calls ``hook`` on every write, so tests can observe the writer thread."""

    def __init__(self, values, hook):
        super().__init__(values)
        self._hook = hook

    def __setitem__(self, index, value):
        self._hook(index, value)
        super().__setitem__(index, value)


def hooked(rows, cols, hook):
    return [HookRow([0] * cols, hook) for _ in range(rows)]


def test_paints_four_quadrants_of_even_matrix():
    matrix = blank(4, 4)
    divide_and_paint(matrix, COLORS)
    assert matrix == expected(4, 4), "each 2x2 quadrant must hold its own colour"


@pytest.mark.parametrize("rows,cols", [(1, 1), (1, 5), (5, 1), (3, 3), (5, 7)])
def test_odd_and_degenerate_sizes_paint_every_cell_once(rows, cols):
    writes = []
    lock = threading.Lock()
    matrix = []
    for i in range(rows):
        matrix.append(HookRow([0] * cols, lambda j, v, i=i: (lock.acquire(), writes.append((i, j)), lock.release())))
    divide_and_paint(matrix, COLORS)
    assert [list(r) for r in matrix] == expected(rows, cols), f"wrong colours for a {rows}x{cols} matrix"
    assert sorted(writes) == sorted((i, j) for i in range(rows) for j in range(cols)), \
        "every cell must be written exactly once (no overlap, no gap)"


def test_paint_quadrant_fills_only_half_open_region_in_place():
    matrix = blank(4, 5)
    result = paint_quadrant(matrix, 1, 3, 2, 5, "X")
    assert result is None, "paint_quadrant returns nothing"
    for i in range(4):
        for j in range(5):
            inside = 1 <= i < 3 and 2 <= j < 5
            assert matrix[i][j] == ("X" if inside else 0), f"cell ({i},{j}) should be {'painted' if inside else 'untouched'}"


def test_quadrants_run_concurrently_on_worker_threads():
    barrier = threading.Barrier(4)
    threads = set()
    main = threading.get_ident()

    def hook(index, value):
        threads.add(threading.get_ident())
        barrier.wait(timeout=2)  # only passes if four quadrants are in flight at once

    matrix = hooked(2, 2, hook)
    divide_and_paint(matrix, COLORS)
    assert main not in threads, "painting must happen in executor threads, not the calling thread"
    assert len(threads) == 4, "expected one worker thread per quadrant, running at the same time"
    assert [list(r) for r in matrix] == expected(2, 2)


def test_waits_for_slow_quadrant_before_returning():
    def hook(index, value):
        if value == "yellow":
            time.sleep(0.15)

    matrix = hooked(4, 4, hook)
    divide_and_paint(matrix, COLORS)
    assert [list(r) for r in matrix] == expected(4, 4), "divide_and_paint returned before the slow quadrant finished"


def test_task_exception_propagates_to_caller():
    def hook(index, value):
        if value == "green":
            raise RuntimeError("worker failed")

    matrix = hooked(4, 4, hook)
    with pytest.raises(RuntimeError, match="worker failed"):
        divide_and_paint(matrix, COLORS)


def test_does_not_print(capsys):
    divide_and_paint(blank(4, 4), COLORS)
    paint_quadrant(blank(2, 2), 0, 2, 0, 2, "x")
    assert capsys.readouterr().out == "", "the library functions must not print"

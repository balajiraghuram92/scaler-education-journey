def paint_quadrant(matrix, start_row, end_row, start_col, end_col, color):
    """Fill ``matrix[i][j] = color`` for ``start_row <= i < end_row`` and ``start_col <= j < end_col``.

    Modify ``matrix`` in place and return ``None``. Do not print.
    """
    raise NotImplementedError("Implement paint_quadrant")


def divide_and_paint(matrix, colors):
    """Paint the four quadrants of a rectangular ``matrix`` in parallel.

    ``colors`` is ``[top_left, top_right, bottom_left, bottom_right]``.
    Rows are split at ``len(matrix) // 2`` and columns at ``len(matrix[0]) // 2``,
    so every cell of an odd-sized matrix is painted exactly once.

    Requirements:
    - submit one ``paint_quadrant`` task per quadrant to a ``ThreadPoolExecutor``
    - wait for every task before returning
    - an exception raised inside a task must propagate to the caller
    - do not print
    """
    raise NotImplementedError("Implement divide_and_paint")

from __future__ import annotations

from collections.abc import Callable, Iterable


class Outcome[R]:
    """Result of one task, as a frozen, slotted dataclass.

    Fields: ``index: int``, ``value: R | None = None``, ``error: BaseException | None = None``,
    ``cancelled: bool = False``, plus a read-only property ``ok`` that is true only for a
    successful, non-cancelled outcome.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Turn Outcome into a frozen, slotted dataclass")


def run_all[T, R](
    fn: Callable[[T], R],
    items: Iterable[T],
    *,
    max_workers: int = 4,
    fail_fast: bool = False,
) -> list[Outcome[R]]:
    """Run ``fn(item)`` for every item on a thread pool and return one ``Outcome`` per input.

    - the result has the same length and order as ``items``
    - exceptions from ``fn`` are stored in ``Outcome.error`` and never raised
    - ``max_workers < 1`` raises ``ValueError``
    - with ``fail_fast=True``, once a task fails, cancel every task that has not started;
      running tasks finish normally; cancelled items get ``cancelled=True``
    - an empty ``items`` returns ``[]``
    - no ``time.sleep`` and no global state
    """
    raise NotImplementedError("Implement run_all")

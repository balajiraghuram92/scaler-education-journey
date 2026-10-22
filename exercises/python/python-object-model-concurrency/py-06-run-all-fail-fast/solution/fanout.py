from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Outcome[R]:
    index: int
    value: R | None = None
    error: BaseException | None = None
    cancelled: bool = False

    @property
    def ok(self) -> bool:
        return self.error is None and not self.cancelled


def run_all[T, R](
    fn: Callable[[T], R],
    items: Iterable[T],
    *,
    max_workers: int = 4,
    fail_fast: bool = False,
) -> list[Outcome[R]]:
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    work = list(items)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(fn, item) for item in work]
        if fail_fast and futures:
            wait(futures, return_when=FIRST_EXCEPTION)
            for fut in futures:
                fut.cancel()  # no-op for running or finished futures
    outcomes: list[Outcome[R]] = []
    for index, fut in enumerate(futures):
        if fut.cancelled():
            outcomes.append(Outcome(index, cancelled=True))
        elif (exc := fut.exception()) is not None:
            outcomes.append(Outcome(index, error=exc))
        else:
            outcomes.append(Outcome(index, value=fut.result()))
    return outcomes

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass


class PipelineClosed(RuntimeError):
    """Raised when submitting to a pipeline that no longer accepts work."""


@dataclass(frozen=True, slots=True)
class Result[R]:
    seq: int
    value: R | None = None
    error: Exception | None = None


class Pipeline[T, R]:
    _STOP = object()

    def __init__(self, fn: Callable[[T], R], *, workers: int = 4, max_pending: int = 8) -> None:
        if workers < 1 or max_pending < 1:
            raise ValueError("workers and max_pending must be >= 1")
        self._fn = fn
        self._queue: queue.Queue[object] = queue.Queue(maxsize=max_pending)
        self._submit_lock = threading.Lock()
        self._results_lock = threading.Lock()
        self._results: list[Result[R]] = []
        self._seq = 0
        self._closed = False
        self._threads = [
            threading.Thread(target=self._run, name=f"pipeline-{i}", daemon=True)
            for i in range(workers)
        ]
        for t in self._threads:
            t.start()

    def submit(self, item: T, timeout: float | None = None) -> int:
        """Enqueue item; blocks while full. Raises queue.Full on timeout."""
        with self._submit_lock:
            if self._closed:
                raise PipelineClosed("pipeline is closed")
            self._queue.put((self._seq, item), timeout=timeout)
            seq = self._seq
            self._seq += 1
            return seq

    def close(self) -> list[Result[R]]:
        with self._submit_lock:
            if not self._closed:
                self._closed = True
                for _ in self._threads:
                    self._queue.put(self._STOP)
        for t in self._threads:
            t.join()
        with self._results_lock:
            return sorted(self._results, key=lambda r: r.seq)

    def _run(self) -> None:
        while True:
            job = self._queue.get()
            try:
                if job is self._STOP:
                    return
                seq, item = job  # type: ignore[misc]
                try:
                    result = Result(seq, value=self._fn(item))
                except Exception as exc:
                    result = Result(seq, error=exc)
                with self._results_lock:
                    self._results.append(result)
            finally:
                self._queue.task_done()

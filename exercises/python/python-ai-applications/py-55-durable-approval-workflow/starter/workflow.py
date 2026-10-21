from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

END = "__end__"
State = dict[str, object]
Update = dict[str, object]
Node = Callable[[State], Update]
Router = Callable[[State], str]
Reducer = Callable[[object, object], object]


class Ledger:
    """Exactly-once guard for side effects (stand-in for an idempotency key sent to a payments API)."""

    def __init__(self) -> None:
        self._done: dict[str, str] = {}

    def run_once(self, key: str, effect: Callable[[], str]) -> str:
        """Run ``effect`` only if ``key`` has not run before; return the (stored) result."""
        raise NotImplementedError("Implement Ledger.run_once")

    def __len__(self) -> int:
        """Number of distinct keys that ran."""
        raise NotImplementedError("Implement Ledger.__len__")


@dataclass(frozen=True, slots=True)
class RunStatus:
    state: State
    next_node: str | None
    status: Literal["done", "paused"]


class Graph:
    def __init__(self, reducers: dict[str, Reducer] | None = None,
                 store: dict[str, str] | None = None, max_steps: int = 50) -> None:
        """``reducers`` maps a state key to ``(old, new) -> merged`` (default: overwrite).
        ``store`` maps thread id -> checkpoint JSON text (``self.store`` must be that dict)."""
        raise NotImplementedError("Implement Graph.__init__")

    def add_node(self, name: str, fn: Node) -> None:
        raise NotImplementedError("Implement Graph.add_node")

    def add_edge(self, src: str, dst: str) -> None:
        """Static edge; ``dst`` may be ``END``."""
        raise NotImplementedError("Implement Graph.add_edge")

    def add_conditional_edges(self, src: str, router: Router) -> None:
        """``router(state)`` returns the next node name (or ``END``). A target that is not a known
        node raises ``ValueError("... unknown node ...")`` when the edge is followed."""
        raise NotImplementedError("Implement Graph.add_conditional_edges")

    def run(self, thread: str, *, initial: State | None = None, entry: str | None = None,
            update: Update | None = None, interrupt_before: frozenset[str] = frozenset()) -> RunStatus:
        """Run or resume a thread.

        - a new thread needs ``initial`` and ``entry`` (else ``ValueError``); an existing thread
          resumes from ``store[thread]``, a JSON object with ``state``, ``next``, ``paused``, ``cleared``
        - nodes get a deep copy of the state and return an update merged through the reducers;
          write the checkpoint after EVERY node (non-serialisable state raises ``TypeError``)
        - if the next node is in ``interrupt_before`` save a paused checkpoint and return
          status ``"paused"``; resuming merges ``update`` and runs that node ONCE without pausing
          again, even if it crashes and is retried
        - when a node raises, the checkpoint still points at it, so ``run(thread)`` retries it
        - a finished thread returns ``RunStatus(state, None, "done")`` immediately
        - more than ``max_steps`` node executions raises ``RuntimeError("step limit ...")``
        """
        raise NotImplementedError("Implement Graph.run")

from __future__ import annotations

import copy
import json
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
    """Exactly-once guard for side effects. In production the key is sent to the downstream API."""

    def __init__(self) -> None:
        self._done: dict[str, str] = {}

    def run_once(self, key: str, effect: Callable[[], str]) -> str:
        if key not in self._done:
            self._done[key] = effect()
        return self._done[key]

    def __len__(self) -> int:
        return len(self._done)


@dataclass(frozen=True, slots=True)
class RunStatus:
    state: State
    next_node: str | None
    status: Literal["done", "paused"]


class Graph:
    def __init__(self, reducers: dict[str, Reducer] | None = None,
                 store: dict[str, str] | None = None, max_steps: int = 50) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str | Router] = {}
        self._reducers = reducers or {}
        self.store: dict[str, str] = store if store is not None else {}   # thread -> JSON text
        self._max_steps = max_steps

    # --- definition ---
    def add_node(self, name: str, fn: Node) -> None:
        self._nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self._edges[src] = dst

    def add_conditional_edges(self, src: str, router: Router) -> None:
        self._edges[src] = router

    # --- persistence (JSON, so state must be serialisable) ---
    def _save(self, thread: str, state: State, next_node: str | None,
              paused: bool = False, cleared: str | None = None) -> None:
        self.store[thread] = json.dumps(
            {"state": state, "next": next_node, "paused": paused, "cleared": cleared})

    def _load(self, thread: str) -> dict:
        return json.loads(self.store[thread])

    def _merge(self, state: State, update: Update) -> State:
        merged = dict(state)
        for key, value in update.items():
            reducer = self._reducers.get(key)
            merged[key] = reducer(state.get(key), value) if reducer else value
        return merged

    def _next(self, node: str, state: State) -> str:
        edge = self._edges[node]
        target = edge(state) if callable(edge) else edge
        if target != END and target not in self._nodes:
            raise ValueError(f"edge from {node!r} points to unknown node {target!r}")
        return target

    # --- execution ---
    def run(self, thread: str, *, initial: State | None = None, entry: str | None = None,
            update: Update | None = None, interrupt_before: frozenset[str] = frozenset()) -> RunStatus:
        if initial is not None:
            if entry is None:
                raise ValueError("entry node required for a new thread")
            state, node, cleared = initial, entry, None
            self._save(thread, state, node)
        else:
            cp = self._load(thread)
            if cp["next"] is None:
                return RunStatus(cp["state"], None, "done")
            state = self._merge(cp["state"], update or {})
            node = cp["next"]
            cleared = node if cp["paused"] else cp["cleared"]       # approval granted for this node
            if cp["paused"]:
                self._save(thread, state, node, cleared=cleared)

        for _ in range(self._max_steps):
            if node in interrupt_before and cleared != node:
                self._save(thread, state, node, paused=True)
                return RunStatus(state, node, "paused")
            state = self._merge(state, self._nodes[node](copy.deepcopy(state)))
            nxt = self._next(node, state)
            cleared = None
            self._save(thread, state, None if nxt == END else nxt)
            if nxt == END:
                return RunStatus(state, None, "done")
            node = nxt
        raise RuntimeError(f"step limit ({self._max_steps}) exceeded; possible cycle")

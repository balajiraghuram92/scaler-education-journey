from __future__ import annotations

import gc
import sys
import types
import weakref
from typing import Any, TypeVar

T = TypeVar("T")

_SKIP = (type, types.ModuleType, types.FunctionType, types.BuiltinFunctionType)
_VIRTUAL_SLOTS = frozenset({"__dict__", "__weakref__"})


def _slot_names(obj: object) -> list[str]:
    names: list[str] = []
    for cls in type(obj).__mro__:
        slots = cls.__dict__.get("__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        names.extend(s for s in slots if s not in _VIRTUAL_SLOTS)
    return names


def deep_sizeof(obj: Any) -> int:
    """Approximate total bytes reachable from obj, counting each object once."""
    seen: set[int] = set()
    stack: list[Any] = [obj]
    total = 0
    while stack:
        current = stack.pop()
        if id(current) in seen or isinstance(current, _SKIP):
            continue
        seen.add(id(current))
        total += sys.getsizeof(current)
        if isinstance(current, dict):
            stack.extend(current.keys())
            stack.extend(current.values())
        elif isinstance(current, (list, tuple, set, frozenset)):
            stack.extend(current)
        else:
            instance_dict = getattr(current, "__dict__", None)
            if instance_dict is not None:
                stack.append(instance_dict)
            for name in _slot_names(current):
                try:
                    stack.append(getattr(current, name))
                except AttributeError:
                    pass  # slot declared but not assigned
    return total


class LeakProbe:
    """Track objects weakly and report how many are still alive."""

    def __init__(self) -> None:
        self._refs: list[weakref.ref[object]] = []

    def track(self, obj: T) -> T:
        self._refs.append(weakref.ref(obj))
        return obj

    def alive_count(self) -> int:
        gc.collect()
        return sum(1 for ref in self._refs if ref() is not None)

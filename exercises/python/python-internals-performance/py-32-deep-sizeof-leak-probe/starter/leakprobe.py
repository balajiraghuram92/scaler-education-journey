from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


def deep_sizeof(obj: Any) -> int:
    """Approximate total bytes reachable from ``obj`` (sum of ``sys.getsizeof``), counting each object once.

    - follow dict keys and values, list / tuple / set / frozenset items, the instance ``__dict__``, and values
      held in ``__slots__`` (including slots declared on base classes; an unassigned slot must not raise)
    - count every object (by ``id``) at most once, so shared references and cycles are fine
    - do not descend into classes, modules or functions
    - be iterative (explicit stack): a 10,000-deep linked list must not hit the recursion limit
    """
    raise NotImplementedError("Implement deep_sizeof")


class LeakProbe:
    """Track objects weakly and report how many are still alive."""

    def track(self, obj: T) -> T:
        """Remember only a weak reference to ``obj`` and return ``obj``."""
        raise NotImplementedError("Implement LeakProbe.track")

    def alive_count(self) -> int:
        """Run ``gc.collect()`` and return how many tracked objects are still alive."""
        raise NotImplementedError("Implement LeakProbe.alive_count")

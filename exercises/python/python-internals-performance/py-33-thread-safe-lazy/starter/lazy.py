from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")


class lazy(Generic[T]):
    """Non-data descriptor: compute once per instance, thread-safely, cache in ``obj.__dict__``.

    Requirements:
    - usable as a decorator on a method taking only ``self``; do NOT define ``__set__`` (non-data descriptor), so after
      the first access the cached ``obj.__dict__[name]`` wins, assignment overrides it, and ``del obj.name`` invalidates it
    - ``__set_name__`` records the attribute name; the same ``lazy`` under a different name raises ``TypeError``
      (message mentioning "two names")
    - double-checked locking: with 8 threads reading at once the function runs exactly once per instance
    - an exception from the function is not cached; a legitimate ``None`` result IS cached
    - class access (``Report.total``) returns the descriptor itself
    """

    def __init__(self, func: Callable[[Any], T]) -> None:
        self.func = func
        # TODO: also keep what you need for the name and the lock

    def __set_name__(self, owner: type, name: str) -> None:
        """Record ``name``; raise TypeError ("two names") if already bound to a different name."""
        # TODO: implement (must not raise for a normal single binding, class bodies call this at creation)

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> "lazy[T]": ...
    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> T: ...
    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        raise NotImplementedError("Implement __get__")

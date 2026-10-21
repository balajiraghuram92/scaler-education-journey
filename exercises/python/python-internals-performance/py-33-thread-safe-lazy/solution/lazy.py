from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")
_UNSET = object()


class lazy(Generic[T]):
    """Non-data descriptor: compute once per instance, thread-safely, cache in __dict__."""

    def __init__(self, func: Callable[[Any], T]) -> None:
        self.func = func
        self.attrname: str | None = None
        self.__doc__ = func.__doc__
        self._lock = threading.RLock()

    def __set_name__(self, owner: type, name: str) -> None:
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                f"Cannot assign the same lazy to two names: {self.attrname!r} and {name!r}"
            )

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> "lazy[T]": ...
    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> T: ...
    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        if self.attrname is None:
            raise TypeError("lazy used without __set_name__")
        cache = obj.__dict__
        value = cache.get(self.attrname, _UNSET)
        if value is _UNSET:
            with self._lock:
                value = cache.get(self.attrname, _UNSET)  # double-checked
                if value is _UNSET:
                    value = self.func(obj)  # exceptions propagate and are not cached
                    cache[self.attrname] = value
        return value

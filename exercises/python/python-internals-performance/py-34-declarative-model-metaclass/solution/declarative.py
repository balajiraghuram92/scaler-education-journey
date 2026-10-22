from __future__ import annotations

import inspect
from typing import Any

_MISSING: Any = object()


class Field:
    """Non-data descriptor declaring a column; the value lives in the instance __dict__."""

    def __init__(self, column_type: str, *, default: Any = _MISSING) -> None:
        self.column_type = column_type
        self.default = default
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        if self.default is _MISSING:
            raise AttributeError(self.name)
        return self.default


class _Namespace(dict[str, Any]):
    """Class-body namespace that rejects redefinition of non-dunder names."""

    def __setitem__(self, key: str, value: Any) -> None:
        dunder = key.startswith("__") and key.endswith("__")
        if key in self and not dunder:
            raise TypeError(f"duplicate definition of {key!r}")
        super().__setitem__(key, value)


class ModelMeta(type):
    __fields__: dict[str, Field]
    __table__: str

    @classmethod
    def __prepare__(mcs, name: str, bases: tuple[type, ...], **kwargs: Any) -> _Namespace:
        return _Namespace()

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        ns: dict[str, Any],
        *,
        table: str | None = None,
        **kwargs: Any,
    ) -> "ModelMeta":
        cls = super().__new__(mcs, name, bases, dict(ns), **kwargs)
        fields: dict[str, Field] = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "__fields__", {}))
        fields.update({k: v for k, v in ns.items() if isinstance(v, Field)})
        cls.__fields__ = fields
        cls.__table__ = table or name.lower() + "s"
        cls.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
            [
                inspect.Parameter(
                    n,
                    inspect.Parameter.KEYWORD_ONLY,
                    default=inspect.Parameter.empty if f.default is _MISSING else f.default,
                )
                for n, f in fields.items()
            ]
        )
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs: Any) -> None:
        bound = type(self).__signature__.bind(**kwargs)  # type: ignore[attr-defined]
        bound.apply_defaults()
        self.__dict__.update(bound.arguments)

    @classmethod
    def create_sql(cls) -> str:
        cols = ", ".join(f"{n} {f.column_type}" for n, f in cls.__fields__.items())
        return f"CREATE TABLE {cls.__table__} ({cols})"

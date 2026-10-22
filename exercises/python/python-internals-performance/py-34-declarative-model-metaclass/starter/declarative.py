from __future__ import annotations

import inspect
from typing import Any

_MISSING: Any = object()


class Field:
    """Non-data descriptor declaring a column; the value lives in the instance ``__dict__``.

    ``__set_name__`` records the name. Accessed on the class it returns itself; on an instance without a stored
    value it returns ``default`` or raises AttributeError if there is none.
    """

    def __init__(self, column_type: str, *, default: Any = _MISSING) -> None:
        self.column_type = column_type
        self.default = default
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        pass  # TODO: record the name (class bodies call this at class creation, so it must not raise)

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        raise NotImplementedError("Implement Field.__get__")


class ModelMeta(type):
    """Metaclass of ``Model``.

    - ``__prepare__`` (a classmethod) returns a ``dict`` subclass that raises
      ``TypeError("duplicate definition of 'x'")`` when a non-dunder name is assigned twice in one class body
    - ``__new__`` accepts the class keyword ``table=`` (default: lowercase class name + ``"s"``), forwards any other
      keywords to ``type.__new__``, and sets ``cls.__fields__`` (inherited fields first, following the MRO, then the
      own fields of the class, in order), ``cls.__table__`` and ``cls.__signature__`` (an ``inspect.Signature``
      listing the fields as keyword-only parameters whose defaults come from ``Field.default``)
    """

    __fields__: dict[str, Field]
    __table__: str

    # TODO: define __prepare__ and replace this skeleton __new__. Until __new__ accepts ``table=``, subclasses such
    # as ``class Bug(Ticket, table="defects")`` cannot even be created.
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        ns: dict[str, Any],
        *,
        table: str | None = None,
        **kwargs: Any,
    ) -> "ModelMeta":
        return super().__new__(mcs, name, bases, dict(ns), **kwargs)


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs: Any) -> None:
        """Bind ``kwargs`` with ``type(self).__signature__`` (missing / unknown names raise TypeError),
        apply defaults and store the values in the instance ``__dict__``."""
        raise NotImplementedError("Implement Model.__init__")

    @classmethod
    def create_sql(cls) -> str:
        """``CREATE TABLE <table> (<name> <type>, ...)`` in field order."""
        raise NotImplementedError("Implement Model.create_sql")

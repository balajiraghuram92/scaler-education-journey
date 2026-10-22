from __future__ import annotations

from collections.abc import Container
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ValidationError(ValueError):
    """Raised when a field rejects a value."""


class Field(Generic[T]):
    """Data descriptor that validates on write and stores in the instance ``__dict__``.

    - ``__set_name__`` records the attribute name (used in error messages and as the storage key)
    - values live in ``obj.__dict__[name]``, never on the descriptor (it is shared by all instances)
    - ``__get__`` returns the descriptor itself for class access (``obj is None``) and raises AttributeError if unset
    - ``__set__`` stores ``self.validate(value)``
    - ``__delete__`` removes the stored value, AttributeError if absent
    """

    name: str

    def __set_name__(self, owner: type, name: str) -> None:
        # TODO: record the name (class bodies call this at class creation, so it must not raise)
        pass

    def validate(self, value: Any) -> T:
        raise NotImplementedError

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        raise NotImplementedError("Implement Field.__get__")

    def __set__(self, obj: object, value: Any) -> None:
        raise NotImplementedError("Implement Field.__set__")

    def __delete__(self, obj: object) -> None:
        raise NotImplementedError("Implement Field.__delete__")


class BoundedFloat(Field[float]):
    """Accepts ints and floats within ``[low, high]`` (coerced to float); rejects bool and non-numbers.

    Error messages (ValidationError) must include the attribute name and the offending value.
    """

    def __init__(self, low: float, high: float) -> None:
        self.low, self.high = low, high

    def validate(self, value: Any) -> float:
        raise NotImplementedError("Implement BoundedFloat.validate")


class BoundedInt(Field[int]):
    """Accepts only real ints (not bool, not float) within ``[low, high]``."""

    def __init__(self, low: int, high: int) -> None:
        self.low, self.high = low, high

    def validate(self, value: Any) -> int:
        raise NotImplementedError("Implement BoundedInt.validate")


class OneOf(Field[str]):
    """Rejects values outside ``choices``."""

    def __init__(self, choices: Container[str]) -> None:
        self.choices = choices

    def validate(self, value: Any) -> str:
        raise NotImplementedError("Implement OneOf.validate")


class CompletionSettings:
    temperature = BoundedFloat(0.0, 2.0)
    max_tokens = BoundedInt(1, 128_000)
    model = OneOf(("small", "large"))

    def __init__(self, temperature: float, max_tokens: int, model: str) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model

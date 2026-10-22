from __future__ import annotations

from collections.abc import Container
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ValidationError(ValueError):
    """Raised when a field rejects a value."""


class Field(Generic[T]):
    """Data descriptor that validates on write and stores in the instance __dict__."""

    name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def validate(self, value: Any) -> T:
        raise NotImplementedError

    def __get__(self, obj: object | None, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, obj: object, value: Any) -> None:
        obj.__dict__[self.name] = self.validate(value)

    def __delete__(self, obj: object) -> None:
        try:
            del obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None


class BoundedFloat(Field[float]):
    def __init__(self, low: float, high: float) -> None:
        self.low, self.high = low, high

    def validate(self, value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(f"{self.name} must be a number, got {value!r}")
        if not self.low <= value <= self.high:
            raise ValidationError(
                f"{self.name} must be between {self.low} and {self.high}, got {value}"
            )
        return float(value)


class BoundedInt(Field[int]):
    def __init__(self, low: int, high: int) -> None:
        self.low, self.high = low, high

    def validate(self, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(f"{self.name} must be an int, got {value!r}")
        if not self.low <= value <= self.high:
            raise ValidationError(
                f"{self.name} must be between {self.low} and {self.high}, got {value}"
            )
        return value


class OneOf(Field[str]):
    def __init__(self, choices: Container[str]) -> None:
        self.choices = choices

    def validate(self, value: Any) -> str:
        if value not in self.choices:
            raise ValidationError(f"{self.name} must be one of {self.choices}, got {value!r}")
        return value


class CompletionSettings:
    temperature = BoundedFloat(0.0, 2.0)
    max_tokens = BoundedInt(1, 128_000)
    model = OneOf(("small", "large"))

    def __init__(self, temperature: float, max_tokens: int, model: str) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model

from __future__ import annotations

from typing import Any, ClassVar


class UnknownProvider(KeyError):
    """Raised when no provider is registered under the requested name."""


class Provider:
    """Base class: subclasses register themselves at class-creation time."""

    registry: ClassVar[dict[str, type["Provider"]]] = {}
    name: ClassVar[str]

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        key = name if name is not None else cls.__name__.lower()
        if cls.complete is Provider.complete:
            raise TypeError(f"{cls.__name__} must override complete()")
        if key in Provider.registry:
            raise TypeError(f"duplicate provider name {key!r}")
        cls.name = key
        Provider.registry[key] = cls

    def complete(self, prompt: str) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, **config: Any) -> "Provider":
        try:
            provider_cls = Provider.registry[name]
        except KeyError:
            known = ", ".join(sorted(Provider.registry)) or "none"
            raise UnknownProvider(f"unknown provider {name!r}; known: {known}") from None
        return provider_cls(**config)

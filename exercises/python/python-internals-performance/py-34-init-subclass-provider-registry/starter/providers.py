from __future__ import annotations

from typing import Any, ClassVar


class UnknownProvider(KeyError):
    """Raised when no provider is registered under the requested name."""


class Provider:
    """Base class: subclasses register themselves at class-creation time via ``__init_subclass__``.

    - ``class Local(Provider, name="llama")`` registers under ``"llama"``; otherwise under ``cls.__name__.lower()``.
      The key is also stored as ``cls.name``.
    - a subclass that does not override ``complete`` raises ``TypeError`` (mentioning ``complete``) and is NOT registered
    - a name that is already registered raises ``TypeError`` mentioning "duplicate"
    - registration also applies to indirect subclasses; unknown class keywords are forwarded to ``super().__init_subclass__``
    - store the registry on ``Provider`` explicitly (``Provider.registry``), not on ``cls``
    """

    registry: ClassVar[dict[str, type["Provider"]]] = {}
    name: ClassVar[str]

    def complete(self, prompt: str) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, **config: Any) -> "Provider":
        """Instantiate the registered class with ``config`` as keyword arguments.

        Unknown name -> ``UnknownProvider`` whose message lists the known names (``known: a, b``).
        """
        raise NotImplementedError("Implement Provider.create")

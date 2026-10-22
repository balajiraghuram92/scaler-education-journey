import logging
import threading
from collections.abc import Callable, Iterable
from typing import Any, Protocol, TypeVar

log = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


class EntryPointLike(Protocol):
    """The two members of importlib.metadata.EntryPoint that we rely on."""

    name: str

    def load(self) -> Callable[..., Any]: ...


class UnknownProviderError(ValueError):
    """No provider is registered under the requested name."""


class ProviderLoadError(RuntimeError):
    """A discovered plugin could not be imported."""


class ProviderFactory:
    """Simple factory backed by a registry, with lazy plugin entry points.

    - ``register(name)`` is a decorator: it stores the builder callable and returns
      it unchanged. A duplicate name (built-in or pending plugin) raises ValueError
      whose message contains ``already registered``.
    - ``load_entry_points(entry_points)`` records plugins WITHOUT calling ``load()``.
      A name that is already registered (built-in or earlier plugin) is skipped with
      a ``log.warning`` that mentions the name. Returns the list of names added.
    - ``names()`` returns every known name (built-in and pending plugins), sorted.
    - ``create(name, **kwargs)`` resolves the builder (calling a pending plugin's
      ``load()`` exactly once and caching the result) and returns ``builder(**kwargs)``.
      Unknown name -> UnknownProviderError listing the known names. If ``load()``
      fails -> ProviderLoadError (mention the name, chained with ``from``), and the
      other providers stay usable.
    - Concurrent first calls to ``create`` for the same plugin call ``load()`` once.
    """

    def __init__(self) -> None:
        self._builders: dict[str, Callable[..., Any]] = {}
        self._pending: dict[str, EntryPointLike] = {}
        self._lock = threading.Lock()

    def register(self, name: str) -> Callable[[F], F]:
        raise NotImplementedError("Implement register")

    def load_entry_points(self, entry_points: Iterable[EntryPointLike]) -> list[str]:
        raise NotImplementedError("Implement load_entry_points")

    def names(self) -> list[str]:
        raise NotImplementedError("Implement names")

    def create(self, name: str, **kwargs: Any) -> Any:
        raise NotImplementedError("Implement create")

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
    """Simple factory backed by a registry, with lazy plugin entry points."""

    def __init__(self) -> None:
        self._builders: dict[str, Callable[..., Any]] = {}
        self._pending: dict[str, EntryPointLike] = {}
        self._lock = threading.Lock()

    def register(self, name: str) -> Callable[[F], F]:
        def decorator(builder: F) -> F:
            with self._lock:
                if name in self._builders or name in self._pending:
                    raise ValueError(f"provider {name!r} is already registered")
                self._builders[name] = builder
            return builder

        return decorator

    def load_entry_points(self, entry_points: Iterable[EntryPointLike]) -> list[str]:
        """Record plugins without importing them. Built-ins and earlier plugins win."""
        added: list[str] = []
        with self._lock:
            for ep in entry_points:
                if ep.name in self._builders or ep.name in self._pending:
                    log.warning("ignoring plugin %r: name already registered", ep.name)
                    continue
                self._pending[ep.name] = ep
                added.append(ep.name)
        return added

    def names(self) -> list[str]:
        with self._lock:
            return sorted(set(self._builders) | set(self._pending))

    def create(self, name: str, **kwargs: Any) -> Any:
        builder = self._resolve(name)
        return builder(**kwargs)

    def _resolve(self, name: str) -> Callable[..., Any]:
        with self._lock:
            builder = self._builders.get(name)
            if builder is not None:
                return builder
            entry_point = self._pending.get(name)
            if entry_point is None:
                known = sorted(set(self._builders) | set(self._pending))
                raise UnknownProviderError(f"unknown provider {name!r}; known: {known}")
            try:
                builder = entry_point.load()
            except Exception as exc:
                raise ProviderLoadError(f"plugin {name!r} failed to load: {exc}") from exc
            self._builders[name] = builder
            del self._pending[name]
            return builder

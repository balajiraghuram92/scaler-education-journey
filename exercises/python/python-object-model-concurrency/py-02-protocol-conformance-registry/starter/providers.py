import inspect  # noqa: F401
from typing import Callable, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class ETAProvider(Protocol):
    def estimate_minutes(self, origin: str, destination: str) -> float: ...


def conformance_errors(candidate: object, protocol: type) -> list[str]:
    """Return human-readable reasons why ``candidate`` (a class or an instance) does not satisfy ``protocol``.

    For every public function declared on the protocol (skip dunders; ``vars(protocol)`` lists them):
    - ``"missing method: <name>"`` when the candidate has no such attribute
      (check presence with ``inspect.getattr_static`` so properties are not executed)
    - ``"not callable: <name>"`` when the attribute is not callable
    - ``"signature mismatch: <name><expected names> != <actual names>"`` when the positional
      parameter names differ (ignore ``self`` on both sides), for example
      ``signature mismatch: estimate_minutes('origin', 'destination') != ()``
    An empty list means the candidate conforms.
    """
    raise NotImplementedError("Implement conformance_errors")


T = TypeVar("T")


class ProviderRegistry:
    """Plug-in registry that validates providers when they are registered."""

    def __init__(self, protocol: type) -> None:
        raise NotImplementedError("Implement ProviderRegistry.__init__")

    def register(self, name: str) -> Callable[[type[T]], type[T]]:
        """Decorator factory. The decorator returns the class unchanged.

        - ``ValueError`` if ``name`` is already registered
        - ``TypeError("<Class> does not satisfy <Protocol>: <reason>; <reason>")`` when the class does
          not conform. A rejected class must not be stored.
        """
        raise NotImplementedError("Implement ProviderRegistry.register")

    def create(self, name: str, /, *args: object, **kwargs: object) -> object:
        """Instantiate the registered provider with ``*args, **kwargs``.

        An unknown name raises ``KeyError`` whose message lists the known names.
        """
        raise NotImplementedError("Implement ProviderRegistry.create")

    def names(self) -> list[str]:
        """Registered provider names, sorted."""
        raise NotImplementedError("Implement ProviderRegistry.names")

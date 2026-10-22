import inspect
from typing import Callable, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class ETAProvider(Protocol):
    def estimate_minutes(self, origin: str, destination: str) -> float: ...


def _param_names(fn: Callable[..., object], *, skip_self: bool) -> list[str]:
    params = list(inspect.signature(fn).parameters.values())
    if skip_self and params and params[0].name == "self":
        params = params[1:]
    return [p.name for p in params]


def conformance_errors(candidate: object, protocol: type) -> list[str]:
    """Return human-readable reasons why `candidate` does not satisfy `protocol`.

    Checks method presence and positional parameter names, which
    isinstance() on a runtime_checkable protocol does not.
    """
    errors: list[str] = []
    for name, proto_fn in vars(protocol).items():
        if not inspect.isfunction(proto_fn) or name.startswith("__"):
            continue
        if inspect.getattr_static(candidate, name, None) is None:
            errors.append(f"missing method: {name}")
            continue
        impl = getattr(candidate, name)
        if not callable(impl):
            errors.append(f"not callable: {name}")
            continue
        expected = _param_names(proto_fn, skip_self=True)
        actual = _param_names(impl, skip_self=isinstance(candidate, type))
        if expected != actual:
            errors.append(f"signature mismatch: {name}{tuple(expected)} != {tuple(actual)}")
    return errors


T = TypeVar("T")


class ProviderRegistry:
    def __init__(self, protocol: type) -> None:
        self._protocol = protocol
        self._providers: dict[str, type] = {}

    def register(self, name: str) -> Callable[[type[T]], type[T]]:
        def decorator(cls: type[T]) -> type[T]:
            if name in self._providers:
                raise ValueError(f"provider {name!r} already registered")
            errors = conformance_errors(cls, self._protocol)
            if errors:
                raise TypeError(f"{cls.__name__} does not satisfy {self._protocol.__name__}: " + "; ".join(errors))
            self._providers[name] = cls
            return cls

        return decorator

    def create(self, name: str, /, *args: object, **kwargs: object) -> object:
        try:
            cls = self._providers[name]
        except KeyError:
            raise KeyError(f"unknown provider {name!r}; known: {sorted(self._providers)}") from None
        return cls(*args, **kwargs)

    def names(self) -> list[str]:
        return sorted(self._providers)

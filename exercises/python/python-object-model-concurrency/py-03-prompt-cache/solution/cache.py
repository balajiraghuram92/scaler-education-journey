from collections import OrderedDict
from collections.abc import Iterator, Mapping, MutableMapping, Sequence
from types import TracebackType


class PromptKey:
    """Immutable, hashable cache key for an LLM request."""

    __slots__ = ("model", "temperature", "messages")

    def __init__(self, model: str, temperature: float, messages: Sequence[Mapping[str, str]]) -> None:
        frozen = tuple(tuple(sorted(m.items())) for m in messages)
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "temperature", temperature)
        object.__setattr__(self, "messages", frozen)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("PromptKey is immutable")

    def _fields(self) -> tuple[object, ...]:
        return (self.model, self.temperature, self.messages)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PromptKey):
            return NotImplemented
        return self._fields() == other._fields()

    def __hash__(self) -> int:
        return hash(self._fields())

    def __repr__(self) -> str:
        return f"PromptKey(model={self.model!r}, temperature={self.temperature!r}, messages={len(self.messages)})"


class ResponseCache(MutableMapping[PromptKey, str]):
    """Bounded LRU mapping. Reading a key marks it most recently used."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._data: OrderedDict[PromptKey, str] = OrderedDict()

    def __getitem__(self, key: PromptKey) -> str:
        value = self._data[key]
        self._data.move_to_end(key)
        return value

    def __setitem__(self, key: PromptKey, value: str) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        while len(self._data) > self._capacity:
            self._data.popitem(last=False)

    def __delitem__(self, key: PromptKey) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[PromptKey]:
        return iter(list(self._data))                # snapshot: safe while mutating

    def __len__(self) -> int:
        return len(self._data)

    def transaction(self) -> "CacheTransaction":
        return CacheTransaction(self)


class CacheTransaction:
    """Buffers writes; commits them only if the with-block finishes without error."""

    def __init__(self, cache: ResponseCache) -> None:
        self._cache = cache
        self._pending: dict[PromptKey, str] = {}

    def __enter__(self) -> "CacheTransaction":
        return self

    def put(self, key: PromptKey, value: str) -> None:
        self._pending[key] = value

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            for k, v in self._pending.items():
                self._cache[k] = v
        self._pending.clear()
        return False                                  # never swallow errors

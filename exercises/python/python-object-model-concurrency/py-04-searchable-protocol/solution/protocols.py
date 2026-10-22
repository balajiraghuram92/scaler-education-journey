from typing import Protocol, runtime_checkable


@runtime_checkable
class Searchable(Protocol):
    def matches(self, query: str) -> bool:
        ...

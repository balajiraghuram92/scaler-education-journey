from typing import Protocol


class Searchable(Protocol):
    """Structural contract for anything that can be searched.

    Declare ``matches(self, query: str) -> bool`` (body ``...``) and make the protocol usable with
    ``isinstance`` by decorating it with ``@runtime_checkable``.
    """

    def matches(self, query: str) -> bool:
        ...

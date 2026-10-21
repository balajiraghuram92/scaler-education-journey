from typing import Protocol, runtime_checkable


@runtime_checkable
class ETAProvider(Protocol):
    def estimate_minutes(self, origin, destination) -> float:
        ...

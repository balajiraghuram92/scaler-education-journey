from typing import Protocol


class ETAProvider(Protocol):
    """Structural contract for ETA providers.

    Declare ``estimate_minutes(self, origin, destination) -> float`` (body ``...``) and make the
    protocol usable with ``isinstance`` by decorating it with ``@runtime_checkable``.
    """

    def estimate_minutes(self, origin, destination) -> float:
        ...

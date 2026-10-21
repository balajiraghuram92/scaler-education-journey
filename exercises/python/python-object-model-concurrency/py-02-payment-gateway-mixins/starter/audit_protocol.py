from typing import Protocol


class Auditable(Protocol):
    """Anything that can record an audit event.

    Declare ``record_audit(self, event) -> None`` and make the protocol checkable with
    ``isinstance`` using ``@runtime_checkable``.
    """

    def record_audit(self, event) -> None:
        ...

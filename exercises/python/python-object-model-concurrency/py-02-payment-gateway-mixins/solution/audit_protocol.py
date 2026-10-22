from typing import Protocol, runtime_checkable


@runtime_checkable
class Auditable(Protocol):
    def record_audit(self, event) -> None:
        ...

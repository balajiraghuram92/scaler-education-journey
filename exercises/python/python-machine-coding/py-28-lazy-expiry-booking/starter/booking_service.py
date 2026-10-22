import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto


class NotFoundError(LookupError):
    """Unknown show or seat."""


class SeatUnavailableError(RuntimeError):
    """A requested seat cannot be claimed or confirmed."""


class HoldExpiredError(SeatUnavailableError):
    """The hold exists but has lapsed."""


class Status(Enum):
    AVAILABLE = auto()
    BLOCKED = auto()
    BOOKED = auto()


@dataclass
class Seat:
    label: str
    status: Status = Status.AVAILABLE
    holder: str | None = None
    blocked_at: datetime | None = None


class InMemorySeatRepository:
    """Seats per show; a ``threading.Lock`` stands in for the database's atomic conditional update.

    Expiry rule (write it once, in a helper): a BLOCKED seat is expired when ``now - blocked_at > hold`` (strictly).
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement InMemorySeatRepository.__init__")

    def add_show(self, show_id: int, labels: Iterable[str]) -> None:
        """Register a show with AVAILABLE seats (existing labels are kept)."""
        raise NotImplementedError("Implement add_show")

    def claim(self, show_id: int, labels: Iterable[str], user: str, now: datetime, hold: timedelta) -> None:
        """All-or-nothing under the lock. NotFoundError for an unknown show/seat; SeatUnavailableError unless
        every seat is AVAILABLE or BLOCKED-and-expired. On success: BLOCKED, holder=user, blocked_at=now."""
        raise NotImplementedError("Implement claim")

    def confirm(self, show_id: int, labels: Iterable[str], user: str, now: datetime, hold: timedelta) -> None:
        """Every seat must be BLOCKED by ``user``: expired -> HoldExpiredError; held by someone else, BOOKED or
        AVAILABLE -> SeatUnavailableError. On success all become BOOKED; on failure nothing changes."""
        raise NotImplementedError("Implement confirm")

    def raw_status(self, show_id: int) -> dict[str, tuple[Status, str | None]]:
        """The STORED ``{label: (status, holder)}`` (no expiry applied). NotFoundError for an unknown show."""
        raise NotImplementedError("Implement raw_status")


class BookingService:
    """Reads the injected clock once per operation and passes ``now`` down to the repository."""

    def __init__(
        self,
        repo: InMemorySeatRepository,
        clock: Callable[[], datetime],
        hold: timedelta = timedelta(minutes=15),
    ) -> None:
        raise NotImplementedError("Implement BookingService.__init__")

    def hold_seats(self, show_id: int, labels: Iterable[str], user: str) -> None:
        """Duplicate labels count once; an empty list raises ValueError; a naive clock value raises ValueError."""
        raise NotImplementedError("Implement hold_seats")

    def confirm(self, show_id: int, labels: Iterable[str], user: str) -> None:
        raise NotImplementedError("Implement confirm")

    def availability(self, show_id: int) -> dict[str, str]:
        """EFFECTIVE status name per seat: an expired BLOCKED seat is reported as ``"AVAILABLE"``."""
        raise NotImplementedError("Implement availability")

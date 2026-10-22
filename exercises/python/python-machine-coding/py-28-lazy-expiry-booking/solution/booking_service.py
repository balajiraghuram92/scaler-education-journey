import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto


class NotFoundError(LookupError):
    pass


class SeatUnavailableError(RuntimeError):
    pass


class HoldExpiredError(SeatUnavailableError):
    pass


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


def _expired(seat: Seat, now: datetime, hold: timedelta) -> bool:
    return (
        seat.status is Status.BLOCKED
        and seat.blocked_at is not None
        and now - seat.blocked_at > hold
    )


class InMemorySeatRepository:
    def __init__(self) -> None:
        self._shows: dict[int, dict[str, Seat]] = {}
        self._lock = threading.Lock()

    def add_show(self, show_id: int, labels: Iterable[str]) -> None:
        with self._lock:
            seats = self._shows.setdefault(show_id, {})
            for label in labels:
                seats.setdefault(label, Seat(label))

    def _lookup(self, show_id: int, labels: Iterable[str]) -> list[Seat]:
        seats = self._shows.get(show_id)
        if seats is None:
            raise NotFoundError(f"show {show_id} does not exist")
        found: list[Seat] = []
        for label in labels:
            if label not in seats:
                raise NotFoundError(f"seat {label} does not exist in show {show_id}")
            found.append(seats[label])
        return found

    def claim(
        self, show_id: int, labels: Iterable[str], user: str, now: datetime, hold: timedelta
    ) -> None:
        with self._lock:
            seats = self._lookup(show_id, labels)
            for seat in seats:
                if not (seat.status is Status.AVAILABLE or _expired(seat, now, hold)):
                    raise SeatUnavailableError(f"seat {seat.label} is not available")
            for seat in seats:
                seat.status = Status.BLOCKED
                seat.holder = user
                seat.blocked_at = now

    def confirm(
        self, show_id: int, labels: Iterable[str], user: str, now: datetime, hold: timedelta
    ) -> None:
        with self._lock:
            seats = self._lookup(show_id, labels)
            for seat in seats:
                if seat.status is not Status.BLOCKED or seat.holder != user:
                    raise SeatUnavailableError(f"seat {seat.label} is not held by {user}")
                if _expired(seat, now, hold):
                    raise HoldExpiredError(f"hold on seat {seat.label} has expired")
            for seat in seats:
                seat.status = Status.BOOKED

    def raw_status(self, show_id: int) -> dict[str, tuple[Status, str | None]]:
        with self._lock:
            seats = self._shows.get(show_id)
            if seats is None:
                raise NotFoundError(f"show {show_id} does not exist")
            return {label: (s.status, s.holder) for label, s in seats.items()}

    def effective_status(self, show_id: int, now: datetime, hold: timedelta) -> dict[str, str]:
        with self._lock:
            seats = self._shows.get(show_id)
            if seats is None:
                raise NotFoundError(f"show {show_id} does not exist")
            return {
                label: (Status.AVAILABLE if _expired(s, now, hold) else s.status).name
                for label, s in seats.items()
            }


class BookingService:
    def __init__(
        self,
        repo: InMemorySeatRepository,
        clock: Callable[[], datetime],
        hold: timedelta = timedelta(minutes=15),
    ) -> None:
        self.repo = repo
        self.clock = clock
        self.hold = hold

    def _now(self) -> datetime:
        now = self.clock()
        if now.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return now

    @staticmethod
    def _labels(labels: Iterable[str]) -> list[str]:
        unique = sorted(set(labels))
        if not unique:
            raise ValueError("labels must not be empty")
        return unique

    def hold_seats(self, show_id: int, labels: Iterable[str], user: str) -> None:
        self.repo.claim(show_id, self._labels(labels), user, self._now(), self.hold)

    def confirm(self, show_id: int, labels: Iterable[str], user: str) -> None:
        self.repo.confirm(show_id, self._labels(labels), user, self._now(), self.hold)

    def availability(self, show_id: int) -> dict[str, str]:
        return self.repo.effective_status(show_id, self._now(), self.hold)

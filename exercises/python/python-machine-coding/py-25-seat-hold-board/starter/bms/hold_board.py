import itertools
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum

class SeatState(Enum):
    AVAILABLE = 'available'
    HELD = 'held'
    BOOKED = 'booked'

class UnknownSeatError(Exception):
    pass

class SeatUnavailableError(Exception):

    def __init__(self, seat_ids: list[int]) -> None:
        super().__init__(f'seats not available: {seat_ids}')
        self.seat_ids = seat_ids

class HoldExpiredError(Exception):
    """confirm() was called with an unknown, released or expired hold token."""

@dataclass(frozen=True)
class _Hold:
    token: str
    user_id: int
    seat_ids: frozenset[int]
    expires_at: float

class SeatHoldBoard:
    """Seat availability for ONE show: hold with expiry, then confirm (book) or release.

    Holds expire lazily: every operation first purges expired holds, so no background thread is needed
    and the clock can be injected in tests.
    """

    def __init__(self, seat_ids: Iterable[int], hold_seconds: float, clock: Callable[[], float]=time.monotonic) -> None:
        """Keep the seat ids, hold duration and clock; track booked seats, live holds by token, which token owns each held seat, a token generator and ONE threading.Lock created here."""
        raise NotImplementedError('TODO: implement __init__')

    def _purge(self, now: float) -> None:
        """Drop every hold whose expires_at <= now. Call it first in every operation."""
        raise NotImplementedError('TODO: implement _purge')

    def _drop(self, hold: _Hold) -> None:
        """Remove one hold and free its seats."""
        raise NotImplementedError('TODO: implement _drop')

    def state(self, seat_id: int) -> SeatState:
        """Under the lock, purge, then BOOKED, HELD or AVAILABLE. UnknownSeatError for an unknown seat."""
        raise NotImplementedError('TODO: implement state')

    def hold(self, user_id: int, seat_ids: Iterable[int]) -> str:
        """Under the lock, purge expired holds, raise UnknownSeatError for unknown seats and SeatUnavailableError (sorted list of the held or booked ones) if any seat is taken. Otherwise create a hold that expires at clock() + hold_seconds and return its token."""
        raise NotImplementedError('TODO: implement hold')

    def confirm(self, token: str) -> frozenset[int]:
        """Under the lock, purge, then book the seats of the live hold and return them as a frozenset. Unknown, released or expired tokens raise HoldExpiredError and book nothing."""
        raise NotImplementedError('TODO: implement confirm')

    def release(self, token: str) -> None:
        """Under the lock, drop the hold if it exists; otherwise do nothing."""
        raise NotImplementedError('TODO: implement release')

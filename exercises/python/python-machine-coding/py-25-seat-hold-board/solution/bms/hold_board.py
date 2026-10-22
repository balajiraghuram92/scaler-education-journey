import itertools
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum


class SeatState(Enum):
    AVAILABLE = "available"
    HELD = "held"
    BOOKED = "booked"


class UnknownSeatError(Exception):
    pass


class SeatUnavailableError(Exception):
    def __init__(self, seat_ids: list[int]) -> None:
        super().__init__(f"seats not available: {seat_ids}")
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

    def __init__(self, seat_ids: Iterable[int], hold_seconds: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._seats = set(seat_ids)
        self._hold_seconds = hold_seconds
        self._clock = clock
        self._booked: set[int] = set()
        self._holds: dict[str, _Hold] = {}
        self._held_by: dict[int, str] = {}              # seat id -> token of the hold that owns it
        self._tokens = (f"H{n}" for n in itertools.count(1))
        self._lock = threading.Lock()

    def _purge(self, now: float) -> None:
        for hold in [h for h in self._holds.values() if h.expires_at <= now]:
            self._drop(hold)

    def _drop(self, hold: _Hold) -> None:
        del self._holds[hold.token]
        for seat_id in hold.seat_ids:
            del self._held_by[seat_id]

    def state(self, seat_id: int) -> SeatState:
        with self._lock:
            self._purge(self._clock())
            if seat_id not in self._seats:
                raise UnknownSeatError(seat_id)
            if seat_id in self._booked:
                return SeatState.BOOKED
            return SeatState.HELD if seat_id in self._held_by else SeatState.AVAILABLE

    def hold(self, user_id: int, seat_ids: Iterable[int]) -> str:
        wanted = frozenset(seat_ids)
        with self._lock:                                # check and update are one critical section
            now = self._clock()
            self._purge(now)
            unknown = wanted - self._seats
            if unknown:
                raise UnknownSeatError(sorted(unknown))
            taken = sorted(s for s in wanted if s in self._booked or s in self._held_by)
            if taken:
                raise SeatUnavailableError(taken)       # all or nothing: nothing was changed
            hold = _Hold(next(self._tokens), user_id, wanted, now + self._hold_seconds)
            self._holds[hold.token] = hold
            for seat_id in wanted:
                self._held_by[seat_id] = hold.token
            return hold.token

    def confirm(self, token: str) -> frozenset[int]:
        with self._lock:
            now = self._clock()
            self._purge(now)
            hold = self._holds.get(token)
            if hold is None:                            # expired holds were purged above
                raise HoldExpiredError(token)
            self._drop(hold)
            self._booked |= hold.seat_ids
            return hold.seat_ids

    def release(self, token: str) -> None:
        with self._lock:
            hold = self._holds.get(token)
            if hold is not None:
                self._drop(hold)

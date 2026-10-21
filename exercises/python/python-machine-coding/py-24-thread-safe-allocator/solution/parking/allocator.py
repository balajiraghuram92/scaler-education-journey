import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


@dataclass(eq=False)
class Spot:
    number: int
    supported: frozenset[VehicleType]
    status: SpotStatus = SpotStatus.AVAILABLE


class ParkingFullError(Exception):
    pass


class AllocationTimeoutError(Exception):
    """The allocator's lock could not be acquired within the timeout."""


Strategy = Callable[[Sequence[Spot], VehicleType], Spot | None]


def first_fit(spots: Sequence[Spot], vehicle_type: VehicleType) -> Spot | None:
    return next((s for s in spots if s.status is SpotStatus.AVAILABLE and vehicle_type in s.supported), None)


class SpotAllocator:
    """One lock guards the whole collection of spots: the contended resource, not a request attribute."""

    def __init__(self, spots: Sequence[Spot], strategy: Strategy = first_fit) -> None:
        self._spots = list(spots)
        self._strategy = strategy
        self._lock = threading.Lock()                       # created once, shared by every call

    def allocate(self, vehicle_type: VehicleType, timeout: float | None = None) -> Spot:
        if not self._lock.acquire(timeout=-1 if timeout is None else timeout):
            raise AllocationTimeoutError(f"no lock within {timeout} seconds")
        try:
            spot = self._strategy(self._spots, vehicle_type)
            if spot is None:
                raise ParkingFullError(f"no spot for a {vehicle_type.value}")
            spot.status = SpotStatus.OCCUPIED               # check and update are one critical section
            return spot
        finally:
            self._lock.release()

    def release(self, spot: Spot) -> None:
        with self._lock:
            spot.status = SpotStatus.AVAILABLE

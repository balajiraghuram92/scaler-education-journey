import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum

class VehicleType(Enum):
    BIKE = 'bike'
    CAR = 'car'
    TRUCK = 'truck'

class SpotStatus(Enum):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'

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

    def __init__(self, spots: Sequence[Spot], strategy: Strategy=first_fit) -> None:
        """Keep a list of the spots, the strategy and ONE threading.Lock created here."""
        raise NotImplementedError('TODO: implement __init__')

    def allocate(self, vehicle_type: VehicleType, timeout: float | None=None) -> Spot:
        """Acquire the lock (Lock.acquire(timeout=...); no timeout means wait; failure raises AllocationTimeoutError). In a try/finally: ask the strategy for a spot, raise ParkingFullError if None, mark it OCCUPIED, return it. Always release the lock."""
        raise NotImplementedError('TODO: implement allocate')

    def release(self, spot: Spot) -> None:
        """Under the same lock mark the spot AVAILABLE."""
        raise NotImplementedError('TODO: implement release')

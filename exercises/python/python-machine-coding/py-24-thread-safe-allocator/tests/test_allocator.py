import random
import threading

import pytest

from parking.allocator import (
    AllocationTimeoutError,
    ParkingFullError,
    Spot,
    SpotAllocator,
    SpotStatus,
    VehicleType,
    first_fit,
)


def make_spots(count):
    kinds = [frozenset({VehicleType.CAR, VehicleType.TRUCK}), frozenset({VehicleType.BIKE, VehicleType.CAR})]
    return [Spot(n, kinds[n % 2]) for n in range(count)]


def run_threads(targets):
    threads = [threading.Thread(target=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    assert not any(t.is_alive() for t in threads), "a worker thread did not finish"


def test_stress_no_spot_is_ever_handed_out_twice():
    allocator = SpotAllocator(make_spots(100))
    winners, wrong_type, guard = [], [], threading.Lock()
    start = threading.Barrier(16, timeout=10)

    def gate(seed):
        rng = random.Random(seed)
        start.wait()
        for _ in range(20):
            vehicle_type = rng.choice([VehicleType.CAR, VehicleType.TRUCK, VehicleType.BIKE])
            try:
                spot = allocator.allocate(vehicle_type)
            except ParkingFullError:
                continue
            with guard:
                winners.append(spot.number)
                if vehicle_type not in spot.supported:
                    wrong_type.append(spot.number)

    run_threads([lambda s=seed: gate(s) for seed in range(16)])
    assert wrong_type == [], "a spot that does not support the requested type was returned"
    assert len(winners) == len(set(winners)), "a spot number was handed out twice"
    assert len(winners) <= 100


def test_release_makes_a_spot_available_again():
    allocator = SpotAllocator(make_spots(1))
    spot = allocator.allocate(VehicleType.CAR)
    with pytest.raises(ParkingFullError):
        allocator.allocate(VehicleType.CAR)
    allocator.release(spot)
    assert spot.status is SpotStatus.AVAILABLE
    assert allocator.allocate(VehicleType.CAR) is spot


def test_allocate_marks_spot_and_respects_vehicle_type():
    spots = make_spots(2)  # spot 0: car/truck, spot 1: bike/car
    allocator = SpotAllocator(spots)
    truck = allocator.allocate(VehicleType.TRUCK)
    assert truck is spots[0] and truck.status is SpotStatus.OCCUPIED
    with pytest.raises(ParkingFullError):
        allocator.allocate(VehicleType.TRUCK)
    bike = allocator.allocate(VehicleType.BIKE)
    assert bike is spots[1]
    with pytest.raises(ParkingFullError):
        allocator.allocate(VehicleType.CAR)


def test_a_spot_shared_by_two_types_is_never_double_booked():
    spot = Spot(1, frozenset({VehicleType.CAR, VehicleType.TRUCK}))
    allocator = SpotAllocator([spot])
    barrier, results, guard = threading.Barrier(16, timeout=10), [], threading.Lock()

    def claim(vehicle_type):
        barrier.wait()
        try:
            allocator.allocate(vehicle_type)
            outcome = True
        except ParkingFullError:
            outcome = False
        with guard:
            results.append(outcome)

    run_threads([lambda: claim(VehicleType.CAR)] * 8 + [lambda: claim(VehicleType.TRUCK)] * 8)
    assert results.count(True) == 1, "one lock must guard the whole collection, not one lock per type"
    assert results.count(False) == 15


def test_a_blocked_caller_times_out_instead_of_waiting_forever():
    entered, proceed = threading.Event(), threading.Event()
    spots = make_spots(2)

    def slow_strategy(candidates, vehicle_type):
        entered.set()
        proceed.wait(timeout=5)  # holds the allocator's lock while waiting
        return first_fit(candidates, vehicle_type)

    allocator = SpotAllocator(spots, strategy=slow_strategy)
    holder = threading.Thread(target=allocator.allocate, args=(VehicleType.CAR,))
    holder.start()
    assert entered.wait(timeout=5)
    with pytest.raises(AllocationTimeoutError):
        allocator.allocate(VehicleType.CAR, timeout=0.05)
    proceed.set()
    holder.join(timeout=10)
    assert sum(s.status is SpotStatus.OCCUPIED for s in spots) == 1, "the timed-out call must not take a spot"


def test_lock_is_released_after_a_full_lot():
    allocator = SpotAllocator(make_spots(1))
    spot = allocator.allocate(VehicleType.TRUCK)
    with pytest.raises(ParkingFullError):
        allocator.allocate(VehicleType.TRUCK, timeout=1)
    allocator.release(spot)  # would block forever if the failed call kept the lock
    assert allocator.allocate(VehicleType.TRUCK, timeout=1) is spot


def test_lock_is_released_when_the_strategy_raises():
    spots = make_spots(1)
    calls = []

    def flaky(candidates, vehicle_type):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom")
        return first_fit(candidates, vehicle_type)

    allocator = SpotAllocator(spots, strategy=flaky)
    with pytest.raises(RuntimeError):
        allocator.allocate(VehicleType.CAR)
    assert spots[0].status is SpotStatus.AVAILABLE
    assert allocator.allocate(VehicleType.CAR, timeout=1) is spots[0], "lock must be released in a finally"


def test_custom_strategy_is_used():
    spots = make_spots(4)

    def last_fit(candidates, vehicle_type):
        return next((s for s in reversed(candidates)
                     if s.status is SpotStatus.AVAILABLE and vehicle_type in s.supported), None)

    allocator = SpotAllocator(spots, strategy=last_fit)
    assert allocator.allocate(VehicleType.CAR) is spots[3]
    assert allocator.allocate(VehicleType.CAR) is spots[2]

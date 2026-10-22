import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from lot.models import SpotStatus
from lot.versioned_repository import (
    StaleWriteError,
    UnknownEntityError,
    VersionedModel,
    VersionedRepository,
)


@dataclass(eq=False)
class VersionedSpot(VersionedModel):
    number: int = 0
    status: SpotStatus = SpotStatus.AVAILABLE


class FakeClock:
    def __init__(self):
        self.now = datetime(2024, 1, 1, 12, 0, 0)

    def __call__(self):
        return self.now

    def advance(self, minutes):
        self.now += timedelta(minutes=minutes)


def test_first_save_assigns_id_and_version_one_and_stored_state_is_isolated():
    repo = VersionedRepository()
    spot = repo.save(VersionedSpot(number=1))
    assert spot.id == 1 and spot.version == 1
    spot.status = SpotStatus.OCCUPIED  # not saved: the repository must not see it
    assert repo.find_by_id(1).status is SpotStatus.AVAILABLE


def test_ids_are_sequential_and_versions_increment():
    repo = VersionedRepository()
    a = repo.save(VersionedSpot(number=1))
    b = repo.save(VersionedSpot(number=2))
    assert (a.id, b.id) == (1, 2)
    again = repo.find_by_id(1)
    repo.save(again)
    assert again.version == 2
    third = repo.find_by_id(1)
    assert third.version == 2
    repo.save(third)
    assert repo.find_by_id(1).version == 3


def test_clock_is_used_for_audit_fields():
    clock = FakeClock()
    repo = VersionedRepository(clock=clock)
    created = clock.now
    spot = repo.save(VersionedSpot(number=1))
    assert spot.created_at == created and spot.last_modified_at == created
    clock.advance(30)
    again = repo.find_by_id(1)
    repo.save(again)
    stored = repo.find_by_id(1)
    assert stored.created_at == created, "created_at never changes"
    assert stored.last_modified_at == created + timedelta(minutes=30)


def test_a_stale_save_is_rejected_and_does_not_overwrite():
    repo = VersionedRepository()
    repo.save(VersionedSpot(number=1))
    first, second = repo.find_by_id(1), repo.find_by_id(1)
    first.status = SpotStatus.OCCUPIED
    repo.save(first)
    second.status = SpotStatus.AVAILABLE
    second.number = 99
    with pytest.raises(StaleWriteError):
        repo.save(second)
    stored = repo.find_by_id(1)
    assert stored.status is SpotStatus.OCCUPIED and stored.number == 1 and stored.version == 2


def test_saving_an_unknown_id_is_an_error():
    repo = VersionedRepository()
    with pytest.raises(UnknownEntityError):
        repo.save(VersionedSpot(id=42, number=1))


def test_find_returns_copies_and_none_for_missing():
    repo = VersionedRepository()
    repo.save(VersionedSpot(number=1))
    a, b = repo.find_by_id(1), repo.find_by_id(1)
    assert a is not b
    a.number = 500
    assert repo.find_by_id(1).number == 1, "mutating a returned object must not change stored state"
    assert repo.find_by_id(404) is None


def test_saved_item_is_copied_on_the_way_in():
    repo = VersionedRepository()
    spot = repo.save(VersionedSpot(number=1))
    spot.number = 77  # changed after save, never saved again
    assert repo.find_by_id(spot.id).number == 1


def test_stale_save_leaves_audit_fields_alone():
    clock = FakeClock()
    repo = VersionedRepository(clock=clock)
    repo.save(VersionedSpot(number=1))
    stale = repo.find_by_id(1)
    winner = repo.find_by_id(1)
    clock.advance(10)
    repo.save(winner)
    modified = repo.find_by_id(1).last_modified_at
    clock.advance(10)
    with pytest.raises(StaleWriteError):
        repo.save(stale)
    after = repo.find_by_id(1)
    assert after.version == 2 and after.last_modified_at == modified


def test_exactly_one_of_many_simultaneous_claims_wins():
    repo = VersionedRepository()
    repo.save(VersionedSpot(number=1))
    barrier, wins, lock = threading.Barrier(8, timeout=10), [], threading.Lock()

    def claim():
        spot = repo.find_by_id(1)  # every thread reads version 1 ...
        barrier.wait()  # ... before any thread writes
        spot.status = SpotStatus.OCCUPIED
        try:
            repo.save(spot)
            outcome = True
        except StaleWriteError:
            outcome = False
        with lock:
            wins.append(outcome)

    threads = [threading.Thread(target=claim) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert len(wins) == 8, "all threads should have finished"
    assert wins.count(True) == 1 and wins.count(False) == 7
    assert repo.find_by_id(1).version == 2

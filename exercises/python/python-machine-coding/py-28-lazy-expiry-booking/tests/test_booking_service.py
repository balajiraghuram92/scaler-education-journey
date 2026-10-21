import threading
from datetime import datetime, timedelta, timezone

import pytest

from booking_service import (
    BookingService,
    HoldExpiredError,
    InMemorySeatRepository,
    NotFoundError,
    SeatUnavailableError,
    Status,
)

T0 = datetime(2026, 11, 1, 14, 0, tzinfo=timezone.utc)


def make(labels=("C3", "C4", "C5")):
    now = [T0]
    repo = InMemorySeatRepository()
    repo.add_show(1, labels)
    return BookingService(repo, clock=lambda: now[0]), repo, now


def test_hold_blocks_seats_for_the_user():
    svc, repo, _ = make()
    svc.hold_seats(1, ["C3", "C4"], "alice")
    assert repo.raw_status(1)["C3"] == (Status.BLOCKED, "alice")
    assert svc.availability(1) == {"C3": "BLOCKED", "C4": "BLOCKED", "C5": "AVAILABLE"}


def test_second_user_is_refused_until_hold_expires_strictly():
    svc, repo, now = make()
    svc.hold_seats(1, ["C4"], "alice")
    now[0] = T0 + timedelta(minutes=15)           # exactly the window: still held
    with pytest.raises(SeatUnavailableError):
        svc.hold_seats(1, ["C4"], "bob")
    now[0] = T0 + timedelta(minutes=15, seconds=1)
    svc.hold_seats(1, ["C4"], "bob")
    assert repo.raw_status(1)["C4"] == (Status.BLOCKED, "bob")


def test_stored_status_stays_stale_but_availability_is_effective():
    svc, repo, now = make()
    svc.hold_seats(1, ["C4"], "alice")
    now[0] = T0 + timedelta(minutes=19)
    assert repo.raw_status(1)["C4"] == (Status.BLOCKED, "alice")
    assert svc.availability(1)["C4"] == "AVAILABLE"


def test_claim_is_all_or_nothing():
    svc, repo, _ = make()
    svc.hold_seats(1, ["C4"], "alice")
    with pytest.raises(SeatUnavailableError):
        svc.hold_seats(1, ["C3", "C4"], "bob")
    assert repo.raw_status(1)["C3"] == (Status.AVAILABLE, None)


def test_unknown_show_or_seat_is_not_found_and_changes_nothing():
    svc, repo, _ = make()
    with pytest.raises(NotFoundError):
        svc.hold_seats(2, ["C3"], "alice")
    with pytest.raises(NotFoundError):
        svc.hold_seats(1, ["C3", "Z9"], "alice")
    assert repo.raw_status(1)["C3"] == (Status.AVAILABLE, None)
    with pytest.raises(NotFoundError):
        svc.availability(99)
    with pytest.raises(NotFoundError):
        svc.confirm(99, ["C3"], "alice")


def test_confirm_rules():
    svc, repo, now = make()
    svc.hold_seats(1, ["C3"], "alice")
    with pytest.raises(SeatUnavailableError):
        svc.confirm(1, ["C3"], "bob")                # not the holder
    svc.confirm(1, ["C3"], "alice")
    assert repo.raw_status(1)["C3"] == (Status.BOOKED, "alice")
    with pytest.raises(SeatUnavailableError):
        svc.confirm(1, ["C4"], "alice")              # never held

    svc.hold_seats(1, ["C5"], "alice")
    now[0] = T0 + timedelta(minutes=20)
    with pytest.raises(HoldExpiredError):
        svc.confirm(1, ["C5"], "alice")
    assert repo.raw_status(1)["C5"] == (Status.BLOCKED, "alice")


def test_input_validation():
    svc, _, _ = make()
    with pytest.raises(ValueError):
        svc.hold_seats(1, [], "alice")
    svc.hold_seats(1, ["C3", "C3"], "alice")
    naive = BookingService(InMemorySeatRepository(), clock=lambda: datetime(2026, 11, 1))
    with pytest.raises(ValueError):
        naive.availability(1)


def test_concurrent_claims_on_an_expired_hold_have_one_winner():
    svc, repo, now = make()
    svc.hold_seats(1, ["C4"], "ghost")
    now[0] = T0 + timedelta(hours=1)
    winners: list[str] = []
    guard = threading.Lock()

    def attempt(user: str) -> None:
        try:
            svc.hold_seats(1, ["C4"], user)
        except SeatUnavailableError:
            return
        with guard:
            winners.append(user)

    threads = [threading.Thread(target=attempt, args=(f"user{i}",)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(winners) == 1
    assert repo.raw_status(1)["C4"] == (Status.BLOCKED, winners[0])


def test_booked_seat_cannot_be_claimed_even_after_the_window():
    svc, repo, now = make()
    svc.hold_seats(1, ["C3"], "alice")
    svc.confirm(1, ["C3"], "alice")
    now[0] = T0 + timedelta(days=1)
    with pytest.raises(SeatUnavailableError):
        svc.hold_seats(1, ["C3"], "bob")
    assert svc.availability(1)["C3"] == "BOOKED"


def test_expired_hold_can_be_reclaimed_by_the_same_user_with_a_fresh_window():
    svc, repo, now = make()
    svc.hold_seats(1, ["C3"], "alice")
    now[0] = T0 + timedelta(minutes=20)
    svc.hold_seats(1, ["C3"], "alice")
    now[0] = T0 + timedelta(minutes=30)  # 10 minutes after the fresh claim
    svc.confirm(1, ["C3"], "alice")
    assert repo.raw_status(1)["C3"] == (Status.BOOKED, "alice")

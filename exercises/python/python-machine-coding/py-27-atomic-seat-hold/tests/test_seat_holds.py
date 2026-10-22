import os
import random
import tempfile
import threading

import pytest

from seat_holds import SeatUnavailableError, hold_seats, init_inventory, seat_states


def new_db(seats=(1, 2, 3, 4, 5, 6)) -> str:
    path = os.path.join(tempfile.mkdtemp(), "cinema.db")
    init_inventory(path, 1, seats)
    return path


def test_successful_hold():
    path = new_db()
    hold_seats(path, 1, [1, 2], "alice")
    states = seat_states(path, 1)
    assert states[1] == ("BLOCKED", "alice")
    assert states[2] == ("BLOCKED", "alice")
    assert states[3] == ("AVAILABLE", None)


def test_hold_is_all_or_nothing():
    path = new_db()
    hold_seats(path, 1, [1, 2], "alice")
    with pytest.raises(SeatUnavailableError):
        hold_seats(path, 1, [2, 3], "bob")
    assert seat_states(path, 1)[3] == ("AVAILABLE", None)
    assert seat_states(path, 1)[2] == ("BLOCKED", "alice")


def test_unknown_seat_counts_as_unavailable():
    path = new_db()
    with pytest.raises(SeatUnavailableError):
        hold_seats(path, 1, [1, 99], "alice")
    assert seat_states(path, 1)[1] == ("AVAILABLE", None)


def test_duplicates_count_once_and_empty_is_rejected():
    path = new_db()
    hold_seats(path, 1, [1, 1, 1], "alice")
    assert seat_states(path, 1)[1] == ("BLOCKED", "alice")
    with pytest.raises(ValueError):
        hold_seats(path, 1, [], "alice")


def test_init_inventory_is_idempotent_and_keeps_state():
    path = new_db()
    hold_seats(path, 1, [1], "alice")
    init_inventory(path, 1, [1, 2, 3, 4, 5, 6, 7])
    states = seat_states(path, 1)
    assert states[1] == ("BLOCKED", "alice")
    assert states[7] == ("AVAILABLE", None)


def test_many_threads_fight_for_the_same_seats_and_exactly_one_wins():
    path = new_db()
    winners: list[str] = []
    guard = threading.Lock()  # protects the local list only

    def attempt(user: str) -> None:
        try:
            hold_seats(path, 1, [1, 2], user)
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
    states = seat_states(path, 1)
    assert states[1] == ("BLOCKED", winners[0])
    assert states[2] == ("BLOCKED", winners[0])


def test_overlapping_requests_never_share_a_seat():
    path = new_db()
    rng = random.Random(7)
    requests = [(f"user{i}", rng.sample(range(1, 7), 2)) for i in range(12)]
    won: dict[str, list[int]] = {}
    guard = threading.Lock()

    def attempt(user: str, seats: list[int]) -> None:
        try:
            hold_seats(path, 1, seats, user)
        except SeatUnavailableError:
            return
        with guard:
            won[user] = seats

    threads = [threading.Thread(target=attempt, args=r) for r in requests]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    claimed = [seat for seats in won.values() for seat in seats]
    assert len(claimed) == len(set(claimed))          # no seat sold twice
    states = seat_states(path, 1)
    for user, seats in won.items():
        for seat in seats:
            assert states[seat] == ("BLOCKED", user)
    blocked = [s for s, (status, _) in states.items() if status == "BLOCKED"]
    assert sorted(blocked) == sorted(claimed)          # no seat blocked by a loser


def test_holds_on_one_show_do_not_touch_another_show():
    path = new_db()
    init_inventory(path, 2, [1, 2])
    hold_seats(path, 1, [1], "alice")
    assert seat_states(path, 2)[1] == ("AVAILABLE", None), "show 2 seat 1 must be untouched"
    hold_seats(path, 2, [1], "bob")
    assert seat_states(path, 1)[1] == ("BLOCKED", "alice")


def test_same_user_cannot_hold_an_already_held_seat_again():
    path = new_db()
    hold_seats(path, 1, [1], "alice")
    with pytest.raises(SeatUnavailableError):
        hold_seats(path, 1, [1], "alice")


def test_failed_hold_releases_the_write_lock():
    path = new_db()
    with pytest.raises(SeatUnavailableError):
        hold_seats(path, 1, [1, 99], "alice")
    # if the failed call leaked its transaction or connection, this would block or raise
    hold_seats(path, 1, [1], "bob")
    assert seat_states(path, 1)[1] == ("BLOCKED", "bob")

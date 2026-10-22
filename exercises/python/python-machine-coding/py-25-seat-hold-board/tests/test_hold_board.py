import threading

import pytest

from bms.hold_board import (
    HoldExpiredError,
    SeatHoldBoard,
    SeatState,
    SeatUnavailableError,
    UnknownSeatError,
)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make():
    clock = FakeClock()
    return SeatHoldBoard(range(1, 6), hold_seconds=600, clock=clock), clock


def test_hold_is_all_or_nothing():
    board, _ = make()
    board.hold(1, [1, 2])
    with pytest.raises(SeatUnavailableError) as info:
        board.hold(2, [2, 3])
    assert info.value.seat_ids == [2]
    assert board.state(3) is SeatState.AVAILABLE, "seat 3 must not be partially held"


def test_unavailable_error_lists_every_offending_seat():
    board, _ = make()
    board.hold(1, [4])
    board.confirm(board.hold(1, [3]))
    with pytest.raises(SeatUnavailableError) as info:
        board.hold(2, [4, 1, 3])
    assert info.value.seat_ids == [3, 4]
    assert board.state(1) is SeatState.AVAILABLE


def test_unknown_seat_is_rejected():
    board, _ = make()
    with pytest.raises(UnknownSeatError):
        board.hold(1, [99])
    with pytest.raises(UnknownSeatError):
        board.hold(1, [1, 99])
    assert board.state(1) is SeatState.AVAILABLE


def test_expired_holds_release_their_seats_and_cannot_be_confirmed():
    board, clock = make()
    token = board.hold(1, [1, 2])
    clock.now = 600  # exactly at expiry: the hold is over
    assert board.state(1) is SeatState.AVAILABLE
    board.hold(2, [1])  # another user can take the seat now
    with pytest.raises(HoldExpiredError):
        board.confirm(token)
    assert board.state(1) is SeatState.HELD, "the late confirm must not steal the seat back"
    assert board.state(2) is SeatState.AVAILABLE


def test_hold_is_live_until_the_expiry_time():
    board, clock = make()
    token = board.hold(1, [1])
    clock.now = 599.9
    assert board.state(1) is SeatState.HELD
    with pytest.raises(SeatUnavailableError):
        board.hold(2, [1])
    assert board.confirm(token) == frozenset({1})


def test_confirm_books_the_seats_for_good():
    board, clock = make()
    token = board.hold(1, [4, 5])
    assert board.confirm(token) == frozenset({4, 5})
    clock.now = 10_000
    assert board.state(4) is SeatState.BOOKED and board.state(5) is SeatState.BOOKED
    with pytest.raises(SeatUnavailableError):
        board.hold(2, [4])


def test_confirm_with_unknown_or_released_token_fails():
    board, _ = make()
    with pytest.raises(HoldExpiredError):
        board.confirm("nope")
    token = board.hold(1, [3])
    board.release(token)
    with pytest.raises(HoldExpiredError):
        board.confirm(token)
    assert board.state(3) is SeatState.AVAILABLE, "a failed confirm must not book anything"


def test_release_frees_seats_and_is_idempotent():
    board, _ = make()
    token = board.hold(1, [5])
    board.release(token)
    board.release(token)
    board.release("never-issued")
    assert board.state(5) is SeatState.AVAILABLE
    board.hold(2, [5])  # and it can be held again


def test_state_of_unknown_seat():
    board, _ = make()
    with pytest.raises(UnknownSeatError):
        board.state(42)


def test_exactly_one_of_many_simultaneous_holds_wins():
    board, _ = make()
    barrier, wins, guard = threading.Barrier(8, timeout=10), [], threading.Lock()

    def attempt(user_id):
        barrier.wait()
        try:
            board.hold(user_id, [1, 2])
            outcome = True
        except SeatUnavailableError:
            outcome = False
        with guard:
            wins.append(outcome)

    threads = [threading.Thread(target=attempt, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)
    assert len(wins) == 8
    assert wins.count(True) == 1 and wins.count(False) == 7

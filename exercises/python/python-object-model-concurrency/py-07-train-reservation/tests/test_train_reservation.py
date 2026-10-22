import threading

import pytest

from config.trainReservation import TrainReservationSystem


class SlowInt(int):
    """An int whose comparisons and subtraction pause, so a check-then-act race is easy to hit."""

    def _pause(self):
        threading.Event().wait(0.0005)

    def __gt__(self, other):
        self._pause()
        return int.__gt__(self, other)

    def __ge__(self, other):
        self._pause()
        return int.__ge__(self, other)

    def __lt__(self, other):
        self._pause()
        return int.__lt__(self, other)

    def __le__(self, other):
        self._pause()
        return int.__le__(self, other)

    def __rsub__(self, other):
        self._pause()
        return int.__rsub__(self, other)


def make_system():
    return TrainReservationSystem({"1AC": 50, "2AC": 100, "3AC": 150, "Sleeper": 200})


def run_bookers(system, jobs, timeout=20):
    """jobs: list of (seat_type, num_seats). Returns the list of booleans, in completion order."""
    results = []
    lock = threading.Lock()

    def worker(seat_type, num):
        ok = system.reserve_seats(seat_type, num)
        with lock:
            results.append((seat_type, ok))

    threads = [threading.Thread(target=worker, args=job, daemon=True) for job in jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "booking threads did not finish (deadlock?)"
    return results


def test_lock_is_a_reentrant_lock():
    system = make_system()
    assert isinstance(system.lock, type(threading.RLock())), "lock must be a threading.RLock"


def test_reserve_success_failure_and_boundary():
    system = make_system()
    assert system.get_available_seats("1AC") == 50
    assert system.reserve_seats("1AC", 20) is True
    assert system.get_available_seats("1AC") == 30
    assert system.reserve_seats("1AC", 31) is False, "more than available must be refused"
    assert system.get_available_seats("1AC") == 30, "a failed reservation changes nothing"
    assert system.reserve_seats("1AC", 30) is True, "booking exactly the remaining seats is allowed"
    assert system.get_available_seats("1AC") == 0
    assert system.reserve_seats("1AC", 1) is False


def test_seat_types_are_independent():
    system = make_system()
    assert system.reserve_seats("2AC", 40) is True
    assert system.get_available_seats("2AC") == 60
    assert system.get_available_seats("1AC") == 50
    assert system.get_available_seats("3AC") == 150
    assert system.get_available_seats("Sleeper") == 200
    assert system.reserve_seats("1AC", 60) is False
    assert system.get_available_seats("2AC") == 60, "a failure in one type must not touch another"


def test_concurrent_bookings_across_types():
    system = make_system()
    jobs = [("1AC", 5)] * 5 + [("2AC", 10)] * 5 + [("3AC", 35)] * 5
    results = run_bookers(system, jobs)
    assert system.get_available_seats("1AC") == 25, "5 x 5 seats booked from 1AC"
    assert system.get_available_seats("2AC") == 50, "5 x 10 seats booked from 2AC"
    assert system.get_available_seats("3AC") == 10, "four 35-seat bookings fit into 150, the fifth must fail"
    assert [ok for t, ok in results if t == "3AC"].count(True) == 4
    assert system.get_available_seats("Sleeper") == 200


def test_never_goes_negative_when_demand_exceeds_supply():
    system = make_system()
    results = run_bookers(system, [("1AC", 7)] * 20)
    assert [ok for _, ok in results].count(True) == 7, "only 7 bookings of 7 fit into 50 seats"
    assert system.get_available_seats("1AC") == 1


def test_check_and_decrement_are_one_critical_section():
    system = make_system()
    jobs = [("3AC", SlowInt(35)) for _ in range(12)]
    results = run_bookers(system, jobs)
    assert [ok for _, ok in results].count(True) == 4, "overbooked: check and decrement must share one lock"
    assert system.get_available_seats("3AC") == 10


@pytest.mark.parametrize("method,args", [("reserve_seats", ("1AC", 1)), ("get_available_seats", ("1AC",))])
def test_methods_hold_the_lock(method, args):
    system = make_system()
    done = threading.Event()
    t = threading.Thread(target=lambda: (getattr(system, method)(*args), done.set()), daemon=True)
    system.lock.acquire()
    try:
        t.start()
        finished_early = done.wait(0.1)
    finally:
        system.lock.release()
    t.join(5)
    assert done.is_set(), f"{method} never finished after the lock was released"
    assert not finished_early, f"{method} must acquire self.lock before touching the dict"

import threading

from config.movieBooking import MovieTicketBookingSystem, book_seats


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


def run_bookers(system, sizes, wrap=int, timeout=20):
    results = []
    lock = threading.Lock()

    def worker(size):
        ok = system.reserve_seats(wrap(size))
        with lock:
            results.append(ok)

    threads = [threading.Thread(target=worker, args=(s,), daemon=True) for s in sizes]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "booking threads did not finish (deadlock?)"
    return results


def blocked_while_locked(system, method, *args):
    """Call ``method`` from another thread while this thread owns ``system.lock``; report if it blocked."""
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
    return not finished_early


def test_initial_state_and_reentrant_lock():
    system = MovieTicketBookingSystem(100)
    assert system.total_seats == 100
    assert system.available_seats == 100
    assert system.get_available_seats() == 100
    assert isinstance(system.lock, type(threading.RLock())), "lock must be a threading.RLock"


def test_reserve_updates_availability_and_failure_changes_nothing():
    system = MovieTicketBookingSystem(100)
    assert system.reserve_seats(10) is True
    assert system.reserve_seats(5) is True
    assert system.get_available_seats() == 85, "15 seats booked so far"
    assert system.reserve_seats(100) is False, "cannot book more than is available"
    assert system.get_available_seats() == 85, "a failed reservation must not change the count"
    assert system.reserve_seats(50) is True
    assert system.get_available_seats() == 35


def test_exact_boundary_books_last_seats_then_refuses():
    system = MovieTicketBookingSystem(10)
    assert system.reserve_seats(10) is True, "booking exactly the available seats is allowed"
    assert system.get_available_seats() == 0
    assert system.reserve_seats(1) is False
    assert system.get_available_seats() == 0, "never negative"


def test_concurrent_booking_never_overbooks():
    system = MovieTicketBookingSystem(100)
    results = run_bookers(system, [10] * 30)
    assert results.count(True) == 10, "exactly 10 bookings of 10 seats fit into 100 seats"
    assert system.get_available_seats() == 0


def test_mixed_sizes_account_for_every_seat():
    system = MovieTicketBookingSystem(100)
    results = run_bookers(system, [15] * 7)
    assert results.count(True) == 6, "six bookings of 15 fit, the seventh must fail"
    assert system.get_available_seats() == 10


def test_check_and_decrement_are_one_critical_section():
    system = MovieTicketBookingSystem(50)
    results = run_bookers(system, [10] * 20, wrap=SlowInt)
    assert results.count(True) == 5, "overbooked: the availability check and the decrement must share one lock"
    assert system.get_available_seats() == 0


def test_reads_and_reservations_hold_the_lock():
    system = MovieTicketBookingSystem(10)
    assert blocked_while_locked(system, "reserve_seats", 1), "reserve_seats must acquire self.lock"
    assert blocked_while_locked(system, "get_available_seats"), "get_available_seats must acquire self.lock"


def test_book_seats_prints_the_outcome(capsys):
    system = MovieTicketBookingSystem(5)
    book_seats(system, 3)
    book_seats(system, 3)
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == ["Successfully booked 3 seats", "Failed to book 3 seats"]
    assert system.get_available_seats() == 2

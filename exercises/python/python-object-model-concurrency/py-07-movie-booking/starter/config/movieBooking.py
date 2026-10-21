class MovieTicketBookingSystem:
    """Seat booking for a single movie, safe to use from many threads. It must never overbook.

    - ``__init__(total_seats)`` sets ``total_seats``, ``available_seats`` (initially equal)
      and ``lock``, a ``threading.RLock``
    - ``reserve_seats(num_seats)`` takes the lock; if ``num_seats <= available_seats`` it
      decrements ``available_seats`` and returns ``True``, otherwise it changes nothing and
      returns ``False``. The check and the decrement are one critical section.
    - ``get_available_seats()`` returns the current count while holding the lock
    """

    def __init__(self, total_seats):
        raise NotImplementedError("Set total_seats, available_seats and the RLock")

    def reserve_seats(self, num_seats):
        raise NotImplementedError("Implement reserve_seats")

    def get_available_seats(self):
        raise NotImplementedError("Implement get_available_seats")


def book_seats(booking_system, num_seats):
    """Reserve ``num_seats`` and print ``Successfully booked N seats`` or ``Failed to book N seats``."""
    raise NotImplementedError("Implement book_seats")

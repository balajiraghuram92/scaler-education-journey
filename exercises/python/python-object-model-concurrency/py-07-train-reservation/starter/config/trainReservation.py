class TrainReservationSystem:
    """Thread-safe seat reservation for the seat types ``1AC``, ``2AC``, ``3AC`` and ``Sleeper``.

    - ``__init__(initial_seats)`` stores a dict mapping each seat type to its available count
      and creates a ``threading.RLock`` named ``lock``
    - ``reserve_seats(seat_type, num_seats)`` returns ``True`` and decrements that type's count if
      enough seats exist, otherwise returns ``False`` and changes nothing; the check and the
      decrement are one critical section
    - ``get_available_seats(seat_type)`` returns the count for that type
    - both methods hold the lock while touching the dict, and different seat types never
      corrupt each other's counts
    """

    def __init__(self, initial_seats):
        raise NotImplementedError("Store the seat counts and create the RLock")

    def reserve_seats(self, seat_type, num_seats):
        raise NotImplementedError("Implement reserve_seats")

    def get_available_seats(self, seat_type):
        raise NotImplementedError("Implement get_available_seats")

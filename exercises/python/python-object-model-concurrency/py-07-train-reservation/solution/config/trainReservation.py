import threading


class TrainReservationSystem:
    def __init__(self, initial_seats):
        self.available_seats = initial_seats
        self.lock = threading.RLock()  # Reentrant Lock

    def reserve_seats(self, seat_type, num_seats):
        with self.lock:
            if num_seats > self.available_seats[seat_type]:
                return False
            self.available_seats[seat_type] -= num_seats
            return True

    def get_available_seats(self, seat_type):
        with self.lock:
            return self.available_seats[seat_type]

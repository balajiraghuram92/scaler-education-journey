from vehicle import Vehicle


class Car(Vehicle):
    def __init__(self, reg_number, seats):
        super().__init__(reg_number)
        self.seats = seats

    def calculate_fare(self, distance_km):
        return 15 * distance_km

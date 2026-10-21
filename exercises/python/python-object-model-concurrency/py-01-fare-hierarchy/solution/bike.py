from vehicle import Vehicle


class Bike(Vehicle):
    def __init__(self, reg_number):
        super().__init__(reg_number)

    def calculate_fare(self, distance_km):
        return 7 * distance_km

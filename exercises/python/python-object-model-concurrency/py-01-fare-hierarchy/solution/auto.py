from vehicle import Vehicle


class Auto(Vehicle):
    def __init__(self, reg_number):
        super().__init__(reg_number)

    def calculate_fare(self, distance_km):
        return max(30, 11 * distance_km)

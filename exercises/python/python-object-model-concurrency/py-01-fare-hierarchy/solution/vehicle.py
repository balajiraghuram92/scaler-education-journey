class Vehicle:
    def __init__(self, reg_number):
        self.reg_number = reg_number
        self.is_available = True

    def calculate_fare(self, distance_km):
        return 10 * distance_km

from vehicle import Vehicle


class Bike(Vehicle):
    """``Bike(reg_number)``: initialise the parent with ``super().__init__`` and
    charge ``7 * distance_km``."""

    def __init__(self, reg_number):
        raise NotImplementedError("Implement Bike.__init__")

    def calculate_fare(self, distance_km):
        raise NotImplementedError("Implement Bike.calculate_fare")

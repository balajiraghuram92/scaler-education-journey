from vehicle import Vehicle


class Auto(Vehicle):
    """``Auto(reg_number)``: initialise the parent with ``super().__init__`` and
    charge ``max(30, 11 * distance_km)`` (a minimum fare of 30)."""

    def __init__(self, reg_number):
        raise NotImplementedError("Implement Auto.__init__")

    def calculate_fare(self, distance_km):
        raise NotImplementedError("Implement Auto.calculate_fare")

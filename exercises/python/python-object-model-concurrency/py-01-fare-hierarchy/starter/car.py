from vehicle import Vehicle


class Car(Vehicle):
    """``Car(reg_number, seats)``: initialise the parent with ``super().__init__``,
    store ``seats``, and charge ``15 * distance_km``."""

    def __init__(self, reg_number, seats):
        raise NotImplementedError("Implement Car.__init__")

    def calculate_fare(self, distance_km):
        raise NotImplementedError("Implement Car.calculate_fare")

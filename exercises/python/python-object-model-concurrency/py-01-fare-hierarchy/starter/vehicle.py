class Vehicle:
    """Base vehicle of the fleet.

    - ``Vehicle(reg_number)`` sets ``self.reg_number`` and ``self.is_available = True``.
    - ``calculate_fare(distance_km)`` returns ``10 * distance_km``.
    """

    def __init__(self, reg_number):
        raise NotImplementedError("Implement Vehicle.__init__")

    def calculate_fare(self, distance_km):
        raise NotImplementedError("Implement Vehicle.calculate_fare")

from vehicle import Vehicle


class CommercialVehicle(Vehicle):
    """``CommercialVehicle(license_type, **kwargs)``: consume only ``license_type``,
    store it, and forward everything else with ``super().__init__(**kwargs)``.

    ``get_priority_score()`` returns 30.
    """

    def __init__(self, license_type, **kwargs):
        raise NotImplementedError("Implement CommercialVehicle.__init__")

    def get_priority_score(self):
        raise NotImplementedError("Implement CommercialVehicle.get_priority_score")

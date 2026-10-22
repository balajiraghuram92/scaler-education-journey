from vehicle import Vehicle


class ElectricVehicle(Vehicle):
    """``ElectricVehicle(battery_capacity, **kwargs)``: consume only ``battery_capacity``,
    store it, and forward everything else with ``super().__init__(**kwargs)``.

    ``get_priority_score()`` returns 20.
    """

    def __init__(self, battery_capacity, **kwargs):
        raise NotImplementedError("Implement ElectricVehicle.__init__")

    def get_priority_score(self):
        raise NotImplementedError("Implement ElectricVehicle.get_priority_score")

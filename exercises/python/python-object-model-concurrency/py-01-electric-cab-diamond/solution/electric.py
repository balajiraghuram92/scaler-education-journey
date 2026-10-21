from vehicle import Vehicle


class ElectricVehicle(Vehicle):
    def __init__(self, battery_capacity, **kwargs):
        self.battery_capacity = battery_capacity
        super().__init__(**kwargs)

    def get_priority_score(self):
        return 20

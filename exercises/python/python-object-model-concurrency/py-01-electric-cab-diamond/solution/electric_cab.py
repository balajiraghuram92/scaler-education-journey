from electric import ElectricVehicle
from commercial import CommercialVehicle


class ElectricCab(ElectricVehicle, CommercialVehicle):
    def __init__(self, reg_number, battery_capacity, license_type):
        super().__init__(
            reg_number=reg_number,
            battery_capacity=battery_capacity,
            license_type=license_type,
        )

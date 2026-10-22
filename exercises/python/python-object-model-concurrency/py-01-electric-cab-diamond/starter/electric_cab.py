from electric import ElectricVehicle
from commercial import CommercialVehicle


class ElectricCab(ElectricVehicle, CommercialVehicle):
    """``ElectricCab(reg_number, battery_capacity, license_type)``.

    Pass everything to the next class in the MRO by keyword through ``super().__init__``
    so that ``Vehicle.__init__`` runs exactly once.
    """

    def __init__(self, reg_number, battery_capacity, license_type):
        raise NotImplementedError("Implement ElectricCab.__init__")

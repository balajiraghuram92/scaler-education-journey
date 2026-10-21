from vehicle import Vehicle


class CommercialVehicle(Vehicle):
    def __init__(self, license_type, **kwargs):
        self.license_type = license_type
        super().__init__(**kwargs)

    def get_priority_score(self):
        return 30

class Vehicle:
    def __init__(self, reg_number, **kwargs):
        self.reg_number = reg_number
        super().__init__(**kwargs)

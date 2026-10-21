class Vehicle:
    """Root of the diamond.

    ``Vehicle(reg_number, **kwargs)`` stores ``reg_number`` and then continues the
    cooperative chain with ``super().__init__(**kwargs)``.
    """

    def __init__(self, reg_number, **kwargs):
        raise NotImplementedError("Implement Vehicle.__init__")

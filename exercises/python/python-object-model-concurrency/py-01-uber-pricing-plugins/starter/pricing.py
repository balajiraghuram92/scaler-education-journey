class BaseFare:
    """End of the MRO chain.

    - ``__init__(**kwargs)`` forwards ``**kwargs`` with ``super().__init__(**kwargs)``.
    - ``calculate_fare(distance)`` returns ``10 * distance``.
    """

    def __init__(self, **kwargs):
        raise NotImplementedError("Implement BaseFare.__init__")

    def calculate_fare(self, distance):
        raise NotImplementedError("Implement BaseFare.calculate_fare")


class SurgeMixin:
    """``SurgeMixin(multiplier)``: ``calculate_fare`` multiplies the fare from ``super()`` by ``multiplier``.

    The initialiser keeps its own argument and forwards the rest cooperatively.
    """

    def __init__(self, multiplier, **kwargs):
        raise NotImplementedError("Implement SurgeMixin.__init__")

    def calculate_fare(self, distance):
        raise NotImplementedError("Implement SurgeMixin.calculate_fare")


class DiscountMixin:
    """``DiscountMixin(percent)``: ``calculate_fare`` subtracts ``percent`` percent from the fare from ``super()``."""

    def __init__(self, percent, **kwargs):
        raise NotImplementedError("Implement DiscountMixin.__init__")

    def calculate_fare(self, distance):
        raise NotImplementedError("Implement DiscountMixin.calculate_fare")


class TaxMixin:
    """``TaxMixin(rate)``: ``calculate_fare`` adds ``rate`` percent to the fare from ``super()``."""

    def __init__(self, rate, **kwargs):
        raise NotImplementedError("Implement TaxMixin.__init__")

    def calculate_fare(self, distance):
        raise NotImplementedError("Implement TaxMixin.calculate_fare")


class FinalFare(TaxMixin, DiscountMixin, SurgeMixin, BaseFare):
    """``FinalFare(multiplier, percent, rate)``: initialise every base cooperatively, by keyword,
    through a single ``super().__init__`` call.

    For distance 10, multiplier 2, percent 10 and rate 5 the fare is 189.
    """

    def __init__(self, multiplier, percent, rate):
        raise NotImplementedError("Implement FinalFare.__init__")

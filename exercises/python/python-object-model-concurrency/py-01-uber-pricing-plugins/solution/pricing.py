class BaseFare:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def calculate_fare(self, distance):
        return 10 * distance


class SurgeMixin:
    def __init__(self, multiplier, **kwargs):
        self.multiplier = multiplier
        super().__init__(**kwargs)

    def calculate_fare(self, distance):
        return super().calculate_fare(distance) * self.multiplier


class DiscountMixin:
    def __init__(self, percent, **kwargs):
        self.percent = percent
        super().__init__(**kwargs)

    def calculate_fare(self, distance):
        fare = super().calculate_fare(distance)
        return fare - (fare * self.percent / 100)


class TaxMixin:
    def __init__(self, rate, **kwargs):
        self.rate = rate
        super().__init__(**kwargs)

    def calculate_fare(self, distance):
        fare = super().calculate_fare(distance)
        return fare + (fare * self.rate / 100)


class FinalFare(TaxMixin, DiscountMixin, SurgeMixin, BaseFare):
    def __init__(self, multiplier, percent, rate):
        super().__init__(
            multiplier=multiplier,
            percent=percent,
            rate=rate,
        )

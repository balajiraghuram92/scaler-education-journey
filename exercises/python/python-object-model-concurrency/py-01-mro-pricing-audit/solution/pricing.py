from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Quote:
    amount: float
    steps: tuple[str, ...] = ()


class BaseFare:
    step_name = "base"

    def __init__(self, *, per_km: float = 10.0, **kwargs: object) -> None:
        self.per_km = per_km
        super().__init__(**kwargs)

    def quote(self, km: float) -> Quote:
        return Quote(self.per_km * km, (BaseFare.step_name,))


class SurgeMixin:
    step_name = "surge"

    def __init__(self, *, multiplier: float, **kwargs: object) -> None:
        self.multiplier = multiplier
        super().__init__(**kwargs)

    def quote(self, km: float) -> Quote:
        q = super().quote(km)
        return replace(q, amount=q.amount * self.multiplier, steps=q.steps + (SurgeMixin.step_name,))


class BookingFeeMixin:
    step_name = "booking_fee"

    def __init__(self, *, fee: float, **kwargs: object) -> None:
        self.fee = fee
        super().__init__(**kwargs)

    def quote(self, km: float) -> Quote:
        q = super().quote(km)
        return replace(q, amount=q.amount + self.fee, steps=q.steps + (BookingFeeMixin.step_name,))


class DiscountMixin:
    step_name = "discount"

    def __init__(self, *, percent: float, **kwargs: object) -> None:
        self.percent = percent
        super().__init__(**kwargs)

    def quote(self, km: float) -> Quote:
        q = super().quote(km)
        return replace(q, amount=q.amount * (1 - self.percent / 100), steps=q.steps + (DiscountMixin.step_name,))


def build_pricer(*mixins: type) -> type[BaseFare]:
    for m in mixins:
        if not isinstance(m, type) or issubclass(m, BaseFare) or not hasattr(m, "step_name"):
            raise TypeError(f"{m!r} is not a pricing mixin")
    name = "Pricer_" + "_".join(m.step_name for m in mixins)
    return type(name, (*mixins, BaseFare), {})  # duplicate mixins raise TypeError


def pricing_order(cls: type) -> list[str]:
    """Step names in the order they are applied (innermost first)."""
    return [c.step_name for c in reversed(cls.__mro__) if "step_name" in vars(c)]

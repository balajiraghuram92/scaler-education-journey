from dataclasses import dataclass, replace  # noqa: F401  (replace is handy for building new Quotes)


@dataclass(frozen=True)
class Quote:
    amount: float
    steps: tuple[str, ...] = ()


class BaseFare:
    """End of the chain: ``step_name = "base"``.

    - ``__init__(self, *, per_km=10.0, **kwargs)`` keeps ``per_km`` and forwards the rest.
    - ``quote(km) -> Quote`` returns ``Quote(per_km * km, ("base",))``.
    """

    step_name = "base"

    def __init__(self, *, per_km: float = 10.0, **kwargs: object) -> None:
        raise NotImplementedError("Implement BaseFare.__init__")

    def quote(self, km: float) -> Quote:
        raise NotImplementedError("Implement BaseFare.quote")


class SurgeMixin:
    """``SurgeMixin(multiplier=...)``, ``step_name = "surge"``.

    ``quote`` asks ``super().quote(km)`` first, multiplies the amount and appends ``"surge"``
    (use the class-qualified name, not ``self.step_name``, which resolves to the leftmost class).
    """

    step_name = "surge"

    def __init__(self, *, multiplier: float, **kwargs: object) -> None:
        raise NotImplementedError("Implement SurgeMixin.__init__")

    def quote(self, km: float) -> Quote:
        raise NotImplementedError("Implement SurgeMixin.quote")


class BookingFeeMixin:
    """``BookingFeeMixin(fee=...)``, ``step_name = "booking_fee"``. Adds ``fee`` to the amount."""

    step_name = "booking_fee"

    def __init__(self, *, fee: float, **kwargs: object) -> None:
        raise NotImplementedError("Implement BookingFeeMixin.__init__")

    def quote(self, km: float) -> Quote:
        raise NotImplementedError("Implement BookingFeeMixin.quote")


class DiscountMixin:
    """``DiscountMixin(percent=...)``, ``step_name = "discount"``. Multiplies the amount by ``(1 - percent / 100)``."""

    step_name = "discount"

    def __init__(self, *, percent: float, **kwargs: object) -> None:
        raise NotImplementedError("Implement DiscountMixin.__init__")

    def quote(self, km: float) -> Quote:
        raise NotImplementedError("Implement DiscountMixin.quote")


def build_pricer(*mixins: type) -> type[BaseFare]:
    """Return ``type(name, (*mixins, BaseFare), {})``.

    Raise ``TypeError`` for a ``BaseFare`` subclass, a non-class, an object without ``step_name``,
    or duplicate mixins.
    """
    raise NotImplementedError("Implement build_pricer")


def pricing_order(cls: type) -> list[str]:
    """Step names in the order they are applied (innermost first), derived from ``cls.__mro__``.

    Hint: read ``vars(c)`` so inherited ``step_name`` attributes are not counted twice.
    """
    raise NotImplementedError("Implement pricing_order")

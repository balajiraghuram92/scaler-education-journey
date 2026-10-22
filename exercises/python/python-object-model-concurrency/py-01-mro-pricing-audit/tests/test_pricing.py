import dataclasses

import pytest

from pricing import (
    BaseFare,
    BookingFeeMixin,
    DiscountMixin,
    Quote,
    SurgeMixin,
    build_pricer,
    pricing_order,
)


def test_surge_applies_after_fee_and_trail_records_order():
    q = build_pricer(SurgeMixin, BookingFeeMixin)(multiplier=2, fee=50).quote(10)
    assert q.amount == 300, "(100 + 50) * 2: the mixin listed first is applied last"
    assert q.steps == ("base", "booking_fee", "surge"), "audit trail lists steps in application order"
    q2 = build_pricer(BookingFeeMixin, SurgeMixin)(multiplier=2, fee=50).quote(10)
    assert q2.amount == 250, "swapping the order gives 100 * 2 + 50"
    assert q2.steps == ("base", "surge", "booking_fee")


def test_three_mixins_and_class_qualified_step_names():
    pricer = build_pricer(DiscountMixin, SurgeMixin, BookingFeeMixin)(multiplier=2, fee=50, percent=10)
    q = pricer.quote(10)
    assert q.amount == pytest.approx(270.0), "((100 + 50) * 2) * 0.9"
    assert q.steps == ("base", "booking_fee", "surge", "discount"), (
        "each mixin must append its OWN step name, not self.step_name"
    )


def test_pricing_order_matches_mro():
    cls = build_pricer(DiscountMixin, SurgeMixin, BookingFeeMixin)
    assert pricing_order(cls) == ["base", "booking_fee", "surge", "discount"]
    assert pricing_order(build_pricer()) == ["base"], "no mixins: only the base step"


def test_pricing_order_does_not_count_inherited_names_twice():
    Pricer = build_pricer(SurgeMixin)

    class Custom(Pricer):
        pass

    assert pricing_order(Custom) == ["base", "surge"], "use vars(c): subclasses inherit step_name"


def test_quote_is_a_frozen_dataclass():
    q = Quote(10.0, ("base",))
    assert dataclasses.is_dataclass(Quote)
    with pytest.raises(dataclasses.FrozenInstanceError):
        q.amount = 1.0
    assert isinstance(build_pricer(SurgeMixin)(multiplier=1).quote(1).steps, tuple), "steps is a tuple"


def test_build_pricer_rejects_invalid_mixins():
    class Plain:
        pass

    class MyFare(BaseFare):
        pass

    for bad in (BaseFare, MyFare, 123, "surge", Plain):
        with pytest.raises(TypeError):
            build_pricer(bad)


def test_build_pricer_rejects_duplicates():
    with pytest.raises(TypeError):
        build_pricer(SurgeMixin, SurgeMixin)


def test_build_pricer_returns_a_basefare_subclass_each_time():
    a, b = build_pricer(SurgeMixin), build_pricer(SurgeMixin)
    assert issubclass(a, BaseFare) and a.__mro__[-2] is BaseFare
    assert a is not b, "no global state: each call builds a new class"


def test_unknown_or_missing_keywords_are_rejected():
    with pytest.raises(TypeError):
        build_pricer(SurgeMixin)(multiplier=2, colour="red")
    with pytest.raises(TypeError):
        build_pricer(SurgeMixin)()
    with pytest.raises(TypeError):
        build_pricer()(unexpected=1)


def test_per_km_override():
    assert build_pricer()(per_km=12).quote(5).amount == 60
    assert build_pricer()().quote(5).amount == 50, "default is 10 per km"

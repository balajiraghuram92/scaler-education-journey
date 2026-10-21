import pytest

from pricing import BaseFare, DiscountMixin, FinalFare, SurgeMixin, TaxMixin


def test_base_fare_is_ten_per_km():
    assert BaseFare().calculate_fare(7) == 70, "base fare is 10 per km"


def test_final_fare_matches_worked_example():
    fare = FinalFare(multiplier=2, percent=10, rate=5).calculate_fare(10)
    assert fare == pytest.approx(189.0), "((10*10)*2) * 0.9 * 1.05 = 189"


def test_final_fare_mro_order():
    assert [c.__name__ for c in FinalFare.mro()] == [
        "FinalFare", "TaxMixin", "DiscountMixin", "SurgeMixin", "BaseFare", "object",
    ]


def test_each_mixin_alone():
    class OnlySurge(SurgeMixin, BaseFare):
        pass

    class OnlyDiscount(DiscountMixin, BaseFare):
        pass

    class OnlyTax(TaxMixin, BaseFare):
        pass

    assert OnlySurge(multiplier=3).calculate_fare(10) == pytest.approx(300), "surge multiplies"
    assert OnlyDiscount(percent=25).calculate_fare(10) == pytest.approx(75), "discount subtracts a percentage"
    assert OnlyTax(rate=10).calculate_fare(10) == pytest.approx(110), "tax adds a percentage"


def test_mixins_call_super_so_order_follows_the_class_statement():
    class Flat5:
        def calculate_fare(self, distance):
            return super().calculate_fare(distance) + 5

    class FlatThenSurge(SurgeMixin, Flat5, BaseFare):
        pass

    class SurgeThenFlat(Flat5, SurgeMixin, BaseFare):
        pass

    assert FlatThenSurge(multiplier=2).calculate_fare(10) == 210, "(100 + 5) * 2: Surge is outermost"
    assert SurgeThenFlat(multiplier=2).calculate_fare(10) == 205, "100 * 2 + 5: Flat is outermost"


def test_initialisers_store_their_own_arguments():
    fare = FinalFare(multiplier=2, percent=10, rate=5)
    assert (fare.multiplier, fare.percent, fare.rate) == (2, 10, 5)


def test_each_initialiser_runs_once(monkeypatch):
    calls = []
    original = BaseFare.__init__

    def counting(self, **kwargs):
        calls.append(dict(kwargs))
        original(self, **kwargs)

    monkeypatch.setattr(BaseFare, "__init__", counting)
    FinalFare(multiplier=2, percent=10, rate=5)
    assert calls == [{}], f"BaseFare.__init__ must run once with no leftover keywords, got {calls}"


def test_unknown_keyword_is_rejected():
    class Priced(SurgeMixin, BaseFare):
        pass

    with pytest.raises(TypeError):
        Priced(multiplier=2, colour="red")


def test_fare_scales_with_distance_and_zero():
    pricing = FinalFare(multiplier=1, percent=0, rate=0)
    assert pricing.calculate_fare(0) == 0
    assert pricing.calculate_fare(3.5) == pytest.approx(35.0)

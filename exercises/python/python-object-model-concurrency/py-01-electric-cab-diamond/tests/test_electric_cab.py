import pytest

from commercial import CommercialVehicle
from electric import ElectricVehicle
from electric_cab import ElectricCab
from vehicle import Vehicle


def test_cab_stores_every_argument():
    cab = ElectricCab("EC101", 75, "Commercial")
    assert cab.reg_number == "EC101", "reg_number must reach Vehicle.__init__"
    assert cab.battery_capacity == 75, "battery_capacity must be stored by ElectricVehicle"
    assert cab.license_type == "Commercial", "license_type must be stored by CommercialVehicle"


def test_mro_order():
    assert ElectricCab.mro() == [ElectricCab, ElectricVehicle, CommercialVehicle, Vehicle, object], (
        "ElectricCab must inherit (ElectricVehicle, CommercialVehicle)"
    )


def test_priority_score_comes_from_electric_vehicle():
    assert ElectricCab("EC1", 50, "Commercial").get_priority_score() == 20, "ElectricVehicle precedes CommercialVehicle in the MRO"


def test_commercial_vehicle_keeps_its_own_score():
    assert CommercialVehicle(license_type="Taxi", reg_number="C1").get_priority_score() == 30


def test_vehicle_init_runs_exactly_once(monkeypatch):
    calls = []
    original = Vehicle.__init__

    def counting(self, *args, **kwargs):
        calls.append(kwargs.get("reg_number", args[0] if args else None))
        original(self, *args, **kwargs)

    monkeypatch.setattr(Vehicle, "__init__", counting)
    ElectricCab("EC1", 50, "Commercial")
    assert calls == ["EC1"], f"Vehicle.__init__ must run exactly once, ran {len(calls)} times"


def test_each_class_consumes_only_its_own_arguments():
    ev = ElectricVehicle(battery_capacity=40, reg_number="E1")
    assert (ev.battery_capacity, ev.reg_number) == (40, "E1")
    assert not hasattr(ev, "license_type"), "ElectricVehicle must not touch license_type"
    cv = CommercialVehicle(license_type="Taxi", reg_number="C1")
    assert (cv.license_type, cv.reg_number) == ("Taxi", "C1")
    assert not hasattr(cv, "battery_capacity"), "CommercialVehicle must not touch battery_capacity"


def test_unknown_keyword_reaches_object_and_fails():
    with pytest.raises(TypeError):
        ElectricVehicle(battery_capacity=1, reg_number="X", colour="red")


def test_works_with_a_third_cooperative_class_in_the_chain():
    seen = []

    class Tracked(Vehicle):
        def __init__(self, **kwargs):
            seen.append("tracked")
            super().__init__(**kwargs)

    class Fleet(ElectricVehicle, Tracked):
        pass

    f = Fleet(battery_capacity=10, reg_number="F1")
    assert seen == ["tracked"] and f.reg_number == "F1", (
        "ElectricVehicle must forward **kwargs to the next class in the MRO, not to Vehicle by name"
    )

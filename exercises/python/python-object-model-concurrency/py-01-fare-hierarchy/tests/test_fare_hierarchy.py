import pytest

from auto import Auto
from bike import Bike
from car import Car
from vehicle import Vehicle


def test_base_vehicle_defaults_and_fare():
    v = Vehicle("V1")
    assert v.reg_number == "V1", "Vehicle must store reg_number"
    assert v.is_available is True, "a new Vehicle is available"
    assert v.calculate_fare(5) == 50, "base fare is 10 per km"


def test_car_fare_and_seats():
    car = Car("CAR101", 4)
    assert car.seats == 4, "Car must store seats"
    assert car.calculate_fare(5) == 75, "car fare is 15 per km"


def test_bike_fare():
    assert Bike("BIKE101").calculate_fare(5) == 35, "bike fare is 7 per km"


def test_auto_fare_above_minimum():
    assert Auto("AUTO101").calculate_fare(5) == 55, "auto fare is 11 per km above the minimum"


def test_auto_minimum_fare_applies():
    assert Auto("A").calculate_fare(1) == 30, "1 km would be 11, the minimum fare is 30"
    assert Auto("A").calculate_fare(0) == 30, "minimum fare applies even for zero distance"


def test_subclasses_initialise_parent_via_super():
    for vehicle in (Car("C", 2), Bike("B"), Auto("A")):
        assert vehicle.reg_number in ("C", "B", "A"), "subclass must call super().__init__ to set reg_number"
        assert vehicle.is_available is True, "subclass must call super().__init__ to set is_available"


def test_subclasses_are_vehicles_and_override_fare():
    for cls in (Car, Bike, Auto):
        assert issubclass(cls, Vehicle), f"{cls.__name__} must extend Vehicle"
        assert "calculate_fare" in vars(cls), f"{cls.__name__} must override calculate_fare"


def test_polymorphic_loop_over_mixed_fleet():
    fleet = [Car("CAR101", 4), Bike("BIKE101"), Auto("AUTO101")]
    assert [v.calculate_fare(5) for v in fleet] == [75, 35, 55], "one loop must pick each subclass's rule"


def test_dispatch_does_not_use_isinstance_for_new_subclass():
    class Limo(Vehicle):
        def calculate_fare(self, distance_km):
            return 99

    assert Limo("L").calculate_fare(1) == 99
    assert [v.calculate_fare(1) for v in (Limo("L"), Bike("B"))] == [99, 7]

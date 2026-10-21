import pytest

from controllers.parking_lot_controller import ParkingLotController
from dtos.get_parking_lot_capacity_request_dto import GetParkingLotCapacityRequestDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from models.gate import Gate
from models.gate_type import GateType
from models.parking_floor import ParkingFloor
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus as S
from models.vehicle_type import VehicleType as V
from repositories.parking_lot_repository_impl import ParkingLotRepositoryImpl
from services.parking_lot_service_impl import ParkingLotServiceImpl


def spot(vt, status=S.AVAILABLE):
    return ParkingSpot(supported_vehicle_type=vt, status=status)


class World:
    def __init__(self):
        self.f1 = ParkingFloor(id=11, floor_number=1, spots=[
            spot(V.CAR), spot(V.CAR), spot(V.CAR, S.OCCUPIED), spot(V.BIKE), spot(V.CAR, S.OUT_OF_SERVICE)])
        self.f2 = ParkingFloor(id=12, floor_number=2, spots=[spot(V.CAR), spot(V.EV_CAR), spot(V.BIKE), spot(V.BIKE)])
        self.gate = Gate(id=5, gate_type=GateType.ENTRY)
        self.repo = ParkingLotRepositoryImpl()
        self.lot = self.repo.save(ParkingLot(name="L", parking_floors=[self.f1, self.f2], gates=[self.gate]))
        self.service = ParkingLotServiceImpl(self.repo)
        self.controller = ParkingLotController(self.service)


def request(lot_id, floors=None, types=None):
    return GetParkingLotCapacityRequestDto(lot_id, floors, types)


def test_no_filters_counts_all_types_on_all_floors():
    w = World()
    result = w.service.get_parking_lot_capacity(w.lot.id)
    assert set(result) == {w.f1, w.f2}
    expected_types = {t.name for t in V}
    assert set(result[w.f1]) == expected_types and set(result[w.f2]) == expected_types
    assert result[w.f1]["CAR"] == 2 and result[w.f1]["BIKE"] == 1 and result[w.f1]["TRUCK"] == 0
    assert result[w.f2]["CAR"] == 1 and result[w.f2]["BIKE"] == 2 and result[w.f2]["EV_CAR"] == 1


def test_only_available_spots_count():
    w = World()
    result = w.service.get_parking_lot_capacity(w.lot.id, vehicle_types=[V.CAR])
    assert result[w.f1] == {"CAR": 2}, "one occupied and one out-of-service car spot must not count"


def test_floor_filter():
    w = World()
    result = w.service.get_parking_lot_capacity(w.lot.id, parking_floors=[w.f2.id])
    assert list(result) == [w.f2]
    assert set(result[w.f2]) == {t.name for t in V}


def test_vehicle_type_filter():
    w = World()
    result = w.service.get_parking_lot_capacity(w.lot.id, vehicle_types=[V.BIKE, V.EV_CAR])
    assert result[w.f1] == {"BIKE": 1, "EV_CAR": 0}
    assert result[w.f2] == {"BIKE": 2, "EV_CAR": 1}


def test_both_filters():
    w = World()
    result = w.service.get_parking_lot_capacity(w.lot.id, parking_floors=[w.f1.id], vehicle_types=[V.CAR])
    assert result == {w.f1: {"CAR": 2}}


def test_unknown_lot_raises_in_service():
    w = World()
    with pytest.raises(InvalidParkingLotException):
        w.service.get_parking_lot_capacity(999)


def test_controller_success_response():
    w = World()
    res = w.controller.get_parking_lot_capacity(request(w.lot.id, [w.f1.id], ["car", "BIKE"]))
    assert res.response.response_status is ResponseStatus.SUCCESS
    assert res.capacity_map == {w.f1: {"CAR": 2, "BIKE": 1}}
    full = w.controller.get_parking_lot_capacity(request(w.lot.id))
    assert set(full.capacity_map) == {w.f1, w.f2}


def test_controller_failure_responses():
    w = World()
    for req in (request(999), request(0), request(-3), request(w.lot.id, types=["spaceship"])):
        res = w.controller.get_parking_lot_capacity(req)
        assert res.response.response_status is ResponseStatus.FAILURE, f"expected FAILURE for {req.__dict__}"
        assert res.response.message, "a failure needs a message"
        assert res.capacity_map is None
    assert w.controller.get_parking_lot_capacity(None).response.response_status is ResponseStatus.FAILURE


def test_repository_assigns_ids_and_finds_lots():
    repo = ParkingLotRepositoryImpl()
    a = repo.save(ParkingLot(name="a", gates=[Gate(id=1)]))
    b = repo.save(ParkingLot(name="b", gates=[Gate(id=2), Gate(id=3)]))
    assert (a.id, b.id) == (1, 2)
    assert repo.get_parking_lot_by_id(2) is b and repo.get_parking_lot_by_id(9) is None
    assert repo.get_parking_lot_by_gate_id(3) is b and repo.get_parking_lot_by_gate_id(1) is a
    assert repo.get_parking_lot_by_gate_id(99) is None

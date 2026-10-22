from datetime import datetime, timedelta

import pytest

from controllers.ticket_controller import TicketController
from dtos.generate_ticket_request_dto import GenerateTicketRequestDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.parking_spot_not_available_exception import ParkingSpotNotAvailableException
from models.floor_status import FloorStatus
from models.gate import Gate
from models.gate_type import GateType
from models.parking_attendant import ParkingAttendant
from models.parking_floor import ParkingFloor
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus
from models.vehicle_type import VehicleType
from repositories.gate_repository_impl import GateRepositoryImpl
from repositories.parking_lot_repository_impl import ParkingLotRepositoryImpl
from repositories.ticket_repository_impl import TicketRepositoryImpl
from repositories.vehicle_repository_impl import VehicleRepositoryImpl
from services.ticket_service_impl import TicketServiceImpl
from strategies.spot_assignment_strategy_impl import SpotAssignmentStrategyImpl

CAR, BIKE = VehicleType.CAR, VehicleType.BIKE


def spots(*specs):
    """specs: (number, vehicle_type) or (number, vehicle_type, status)."""
    return [ParkingSpot(number=s[0], supported_vehicle_type=s[1],
                        status=s[2] if len(s) > 2 else ParkingSpotStatus.AVAILABLE) for s in specs]


class World:
    def __init__(self, floors):
        self.gates = GateRepositoryImpl()
        self.lots = ParkingLotRepositoryImpl()
        self.vehicles = VehicleRepositoryImpl()
        self.tickets = TicketRepositoryImpl()
        self.attendant = ParkingAttendant(name="Ravi")
        self.entry = self.gates.save(Gate(gate_number=1, gate_type=GateType.ENTRY, parking_attendant=self.attendant))
        self.exit = self.gates.save(Gate(gate_number=2, gate_type=GateType.EXIT))
        self.lot = self.lots.save(ParkingLot(name="L", parking_floors=floors, gates=[self.entry, self.exit]))
        self.strategy = SpotAssignmentStrategyImpl()
        self.service = TicketServiceImpl(self.gates, self.lots, self.vehicles, self.tickets, self.strategy)
        self.controller = TicketController(self.service)


def floor(number, spot_list, status=FloorStatus.OPERATIONAL):
    return ParkingFloor(floor_number=number, status=status, spots=spot_list)


def test_ticket_is_issued_at_an_entry_gate():
    w = World([floor(1, spots((1, CAR), (2, CAR)))])
    before = datetime.now()
    ticket = w.service.generate_ticket(w.entry.id, "KA01", "car")
    assert ticket.id is not None and w.tickets.get_ticket_by_id(ticket.id) is ticket
    assert ticket.vehicle.registration_number == "KA01"
    assert ticket.parking_spot.number == 1
    assert ticket.parking_spot.status is ParkingSpotStatus.OCCUPIED
    assert ticket.gate is w.entry and ticket.parking_attendant is w.attendant
    assert before - timedelta(seconds=1) <= ticket.entry_time <= datetime.now() + timedelta(seconds=1)


def test_exit_or_unknown_gate_is_rejected():
    w = World([floor(1, spots((1, CAR)))])
    with pytest.raises(InvalidGateException):
        w.service.generate_ticket(w.exit.id, "KA01", "car")
    with pytest.raises(InvalidGateException):
        w.service.generate_ticket(999, "KA01", "car")
    assert w.tickets.get_ticket_by_id(1) is None
    assert w.lot.parking_floors[0].spots[0].status is ParkingSpotStatus.AVAILABLE


def test_vehicle_is_found_or_created():
    w = World([floor(1, spots((1, CAR), (2, CAR)))])
    assert w.vehicles.get_vehicle_by_registration_number("KA01") is None
    first = w.service.generate_ticket(w.entry.id, "KA01", "car")
    assert w.vehicles.get_vehicle_by_registration_number("KA01") is first.vehicle
    assert first.vehicle.vehicle_type is CAR
    second = w.service.generate_ticket(w.entry.id, "KA01", "car")
    assert second.vehicle is first.vehicle, "an existing registration must be reused"
    assert len(w.vehicles._vehicles) == 1


def test_floor_with_fewest_available_spots_is_chosen():
    f1 = floor(1, spots((1, CAR), (2, CAR), (3, CAR)))
    f2 = floor(2, spots((1, CAR), (2, CAR)))
    f3 = floor(3, spots((1, CAR), (2, CAR), (3, CAR), (4, CAR)))
    w = World([f1, f2, f3])
    ticket = w.service.generate_ticket(w.entry.id, "A", "car")
    assert ticket.parking_spot in f2.spots, "floor 2 has the fewest (2) available car spots"


def test_tie_goes_to_lowest_floor_and_nearest_spot():
    f2 = floor(2, spots((7, CAR), (5, CAR)))
    f1 = floor(1, spots((9, CAR), (3, CAR)))
    w = World([f2, f1])  # deliberately not in floor order
    ticket = w.service.generate_ticket(w.entry.id, "A", "car")
    assert ticket.parking_spot is f1.spots[1], "floor 1, spot number 3"


def test_non_operational_floors_and_other_types_are_ignored():
    maintenance = floor(1, spots((1, CAR)), FloorStatus.UNDER_MAINTENANCE)
    busy = floor(2, spots((1, CAR, ParkingSpotStatus.OCCUPIED), (2, BIKE), (3, CAR, ParkingSpotStatus.OUT_OF_SERVICE)))
    good = floor(3, spots((1, BIKE), (2, CAR), (3, CAR)))
    w = World([maintenance, busy, good])
    ticket = w.service.generate_ticket(w.entry.id, "A", "car")
    assert ticket.parking_spot is good.spots[1]
    bike = w.service.generate_ticket(w.entry.id, "B", "bike")
    assert bike.parking_spot.supported_vehicle_type is BIKE
    assert bike.parking_spot in busy.spots, "floor 2 has 1 free bike spot, floor 3 has 1: tie goes to floor 2"


def test_no_spot_available_issues_no_ticket():
    w = World([floor(1, spots((1, CAR, ParkingSpotStatus.OCCUPIED)), FloorStatus.OPERATIONAL)])
    with pytest.raises(ParkingSpotNotAvailableException):
        w.service.generate_ticket(w.entry.id, "A", "car")
    with pytest.raises(ParkingSpotNotAvailableException):
        w.service.generate_ticket(w.entry.id, "B", "bike")
    assert w.tickets.get_ticket_by_id(1) is None, "no ticket may be stored"


def test_vehicle_type_string_is_parsed():
    w = World([floor(1, spots((1, CAR), (2, BIKE), (3, VehicleType.EV_CAR)))])
    assert w.service.generate_ticket(w.entry.id, "A", "CAR").vehicle.vehicle_type is CAR
    assert w.service.generate_ticket(w.entry.id, "B", VehicleType.BIKE).vehicle.vehicle_type is BIKE
    assert w.service.generate_ticket(w.entry.id, "C", "ev_car").vehicle.vehicle_type is VehicleType.EV_CAR
    with pytest.raises(ValueError):
        w.service.generate_ticket(w.entry.id, "D", "hoverboard")


def test_controller_success_and_failures():
    w = World([floor(1, spots((1, CAR)))])
    ok = w.controller.generate_ticket(GenerateTicketRequestDto(w.entry.id, "KA01", "car"))
    assert ok.response_status is ResponseStatus.SUCCESS
    assert ok.ticket.parking_spot.number == 1
    bad_requests = [
        GenerateTicketRequestDto(w.exit.id, "KA02", "car"),   # exit gate
        GenerateTicketRequestDto(999, "KA02", "car"),          # unknown gate
        GenerateTicketRequestDto(w.entry.id, "KA02", "car"),   # lot is now full
        GenerateTicketRequestDto(w.entry.id, "KA02", "boat"),  # invalid type
    ]
    for req in bad_requests:
        res = w.controller.generate_ticket(req)
        assert res.response_status is ResponseStatus.FAILURE, f"expected FAILURE for gate {req.gate_id} {req.vehicle_type}"
        assert res.ticket is None


def test_strategy_marks_each_assigned_spot_occupied():
    f1 = floor(1, spots((1, CAR), (2, CAR)))
    lot = ParkingLot(parking_floors=[f1])
    strategy = SpotAssignmentStrategyImpl()
    a = strategy.assign_spot(lot, CAR)
    b = strategy.assign_spot(lot, CAR)
    assert (a.number, b.number) == (1, 2)
    assert a.status is ParkingSpotStatus.OCCUPIED and b.status is ParkingSpotStatus.OCCUPIED
    assert strategy.assign_spot(lot, CAR) is None
    assert strategy.assign_spot(ParkingLot(), CAR) is None

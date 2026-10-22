from datetime import datetime

import pytest
from freezegun import freeze_time

from controllers.invoice_controller import InvoiceController
from controllers.ticket_controller import TicketController
from dtos.generate_invoice_request_dto import GenerateInvoiceRequestDto
from dtos.generate_ticket_request_dto import GenerateTicketRequestDto
from dtos.response_status import ResponseStatus
from exceptions.additional_service_not_supported_by_vehicle import AdditionalServiceNotSupportedByVehicle
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.ticket_not_found_exception import TicketNotFoundException
from exceptions.unsupported_additional_service import UnsupportedAdditionalService
from models.additional_service import AdditionalService
from models.gate import Gate
from models.gate_type import GateType
from models.parking_attendant import ParkingAttendant
from models.parking_floor import ParkingFloor
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.parking_spot_status import ParkingSpotStatus
from models.slab import Slab
from models.vehicle_type import VehicleType as V
from repositories.gate_repository_impl import GateRepositoryImpl
from repositories.invoice_repository_impl import InvoiceRepositoryImpl
from repositories.parking_lot_repository_impl import ParkingLotRepositoryImpl
from repositories.slab_repository_impl import SlabRepositoryImpl
from repositories.ticket_repository_impl import TicketRepositoryImpl
from repositories.vehicle_repository_impl import VehicleRepositoryImpl
from services.invoice_service_impl import InvoiceServiceImpl
from services.ticket_service_impl import TicketServiceImpl
from strategies.assign_nearest_available_spot_strategy import AssignNearestAvailableSpotStrategy
from strategies.pricing_strategy_factory import PricingStrategyFactory
from strategies.weekday_pricing_strategy import WeekdayPricingStrategy
from strategies.weekend_pricing_strategy import WeekendPricingStrategy

# 2024-06-03 is a Monday, 2024-06-01 a Saturday, 2024-06-02 a Sunday.
MON = datetime(2024, 6, 3, 10, 0)
SAT = datetime(2024, 6, 1, 10, 0)


def at(base, hours=0, minutes=0):
    return base.replace(hour=base.hour + hours, minute=base.minute + minutes)


def car_slabs(repo):
    for start, end, price in [(0, 2, 20), (2, 4, 30), (4, 6, 40), (6, -1, 50)]:
        repo.save(Slab(start_hour=start, end_hour=end, price=price, vehicle_type=V.CAR))


class World:
    def __init__(self):
        self.attendant = ParkingAttendant(name="Ravi")
        self.gates = GateRepositoryImpl()
        self.entry = self.gates.save(Gate(gate_type=GateType.ENTRY, parking_attendant=self.attendant))
        self.exit = self.gates.save(Gate(gate_type=GateType.EXIT, parking_attendant=self.attendant))
        spots = [ParkingSpot(number=1, supported_vehicle_type=V.CAR), ParkingSpot(number=2, supported_vehicle_type=V.CAR),
                 ParkingSpot(number=3, supported_vehicle_type=V.BIKE), ParkingSpot(number=4, supported_vehicle_type=V.EV_BIKE)]
        self.floor = ParkingFloor(floor_number=1, spots=spots)
        self.lots = ParkingLotRepositoryImpl()
        self.lots.save(ParkingLot(name="L", parking_floors=[self.floor], gates=[self.entry, self.exit]))
        self.vehicles = VehicleRepositoryImpl()
        self.tickets = TicketRepositoryImpl()
        self.slabs = SlabRepositoryImpl()
        car_slabs(self.slabs)
        self.invoices = InvoiceRepositoryImpl()
        self.ticket_service = TicketServiceImpl(self.gates, self.vehicles, AssignNearestAvailableSpotStrategy(),
                                                self.lots, self.tickets)
        self.invoice_service = InvoiceServiceImpl(self.tickets, PricingStrategyFactory(self.slabs), self.gates,
                                                  self.invoices)

    def ticket(self, vehicle_type="car", services=None, reg="KA01"):
        return self.ticket_service.generate_ticket(self.entry.id, reg, vehicle_type, services)


def test_ticket_stores_parsed_additional_services():
    w = World()
    ticket = w.ticket("car", ["CAR_WASH", "car_detailing"])
    assert ticket.additional_services == [AdditionalService.CAR_WASH, AdditionalService.CAR_DETAILING]
    assert w.ticket("bike", None, "KA02").additional_services == []
    assert w.ticket("ev_bike", [AdditionalService.EV_BIKE_CHARGING], "KA03").additional_services == [
        AdditionalService.EV_BIKE_CHARGING]


def test_unsupported_service_for_vehicle_issues_no_ticket():
    w = World()
    with pytest.raises(AdditionalServiceNotSupportedByVehicle):
        w.ticket("bike", ["CAR_WASH"])
    with pytest.raises(AdditionalServiceNotSupportedByVehicle):
        w.ticket("car", ["CAR_WASH", "EV_CAR_CHARGING"])
    assert w.tickets.get_ticket_by_id(1) is None
    assert all(s.status is ParkingSpotStatus.AVAILABLE for s in w.floor.spots), "no spot may be taken"
    with pytest.raises(UnsupportedAdditionalService):
        w.ticket("car", ["TIME_TRAVEL"])
    assert w.tickets.get_ticket_by_id(1) is None


def test_gate_and_ticket_validation_on_invoice():
    w = World()
    ticket = w.ticket()
    with pytest.raises(InvalidGateException):
        w.ticket_service.generate_ticket(w.exit.id, "KA09", "car")
    with pytest.raises(InvalidGateException):
        w.invoice_service.create_invoice(ticket.id, w.entry.id, at(MON, 1))
    with pytest.raises(InvalidGateException):
        w.invoice_service.create_invoice(ticket.id, 999, at(MON, 1))
    with pytest.raises(TicketNotFoundException):
        w.invoice_service.create_invoice(999, w.exit.id, at(MON, 1))
    assert ticket.parking_spot.status is ParkingSpotStatus.OCCUPIED, "failed invoices must not free the spot"


@pytest.mark.parametrize("hours,minutes,expected", [(1, 0, 10.0), (1, 30, 20.0), (2, 1, 30.0), (0, 0, 0.0)])
def test_weekday_pricing_rounds_up_hours(hours, minutes, expected):
    strategy = WeekdayPricingStrategy()
    assert strategy.calculate_amount(MON, at(MON, hours, minutes), V.CAR) == expected
    assert strategy.calculate_amount(MON, at(MON, hours, minutes), V.TRUCK) == expected, "same rate for every type"


@pytest.mark.parametrize("hours,expected", [(0, 0), (1, 20), (2, 40), (3, 70), (4, 100), (5, 140), (6, 180), (7, 230)])
def test_weekend_slab_pricing_for_cars(hours, expected):
    slabs = SlabRepositoryImpl()
    car_slabs(slabs)
    strategy = WeekendPricingStrategy(slabs)
    assert strategy.calculate_amount(SAT, at(SAT, hours), V.CAR) == expected
    assert strategy.calculate_amount(SAT, at(SAT, hours - 1, 30) if hours else SAT, V.CAR) == (
        expected if hours else 0), "a part hour counts as a full hour"


def test_weekend_slabs_are_per_vehicle_type():
    slabs = SlabRepositoryImpl()
    car_slabs(slabs)
    slabs.save(Slab(start_hour=0, end_hour=-1, price=5, vehicle_type=V.BIKE))
    strategy = WeekendPricingStrategy(slabs)
    assert strategy.calculate_amount(SAT, at(SAT, 3), V.BIKE) == 15
    assert strategy.calculate_amount(SAT, at(SAT, 3), V.CAR) == 70
    assert strategy.calculate_amount(SAT, at(SAT, 3), V.TRUCK) == 0, "no slabs for a type means no charge"


def test_invoice_adds_service_fees_to_parking_fee():
    w = World()
    ticket = w.ticket("car", ["CAR_WASH", "CAR_DETAILING"])
    ticket.entry_time = MON
    invoice = w.invoice_service.create_invoice(ticket.id, w.exit.id, at(MON, 1, 30))
    assert invoice.amount == 20 + 200 + 500
    weekend = w.ticket("car", None, "KA05")
    weekend.entry_time = SAT
    assert w.invoice_service.create_invoice(weekend.id, w.exit.id, at(SAT, 3)).amount == 70


def test_invoice_frees_the_spot_and_is_saved():
    w = World()
    ticket = w.ticket()
    ticket.entry_time = MON
    exit_time = at(MON, 2)
    invoice = w.invoice_service.create_invoice(ticket.id, w.exit.id, exit_time)
    assert invoice.id is not None and invoice.ticket is ticket and invoice.gate is w.exit
    assert invoice.exit_time == exit_time and invoice.parking_attendant is w.attendant
    assert ticket.parking_spot.status is ParkingSpotStatus.AVAILABLE
    assert w.ticket(reg="KA77").parking_spot is ticket.parking_spot, "the freed spot can be assigned again"


def test_pricing_strategy_follows_exit_day():
    factory = PricingStrategyFactory(SlabRepositoryImpl())
    assert isinstance(factory.get_pricing_strategy(datetime(2024, 6, 7)), WeekdayPricingStrategy)  # Friday
    assert isinstance(factory.get_pricing_strategy(datetime(2024, 6, 1)), WeekendPricingStrategy)  # Saturday
    assert isinstance(factory.get_pricing_strategy(datetime(2024, 6, 2)), WeekendPricingStrategy)  # Sunday
    assert isinstance(factory.get_pricing_strategy(datetime(2024, 6, 3)), WeekdayPricingStrategy)  # Monday


def test_controllers_translate_errors():
    w = World()
    tickets = TicketController(w.ticket_service)
    invoices = InvoiceController(w.invoice_service)
    with freeze_time("2024-06-01 10:00:00"):
        ok = tickets.generate_ticket(GenerateTicketRequestDto(w.entry.id, "KA01", "car", ["CAR_WASH"]))
        bad = tickets.generate_ticket(GenerateTicketRequestDto(w.entry.id, "KA02", "bike", ["CAR_WASH"]))
    assert ok.response_status is ResponseStatus.SUCCESS and ok.ticket.additional_services == [AdditionalService.CAR_WASH]
    assert bad.response_status is ResponseStatus.FAILURE and bad.ticket is None
    with freeze_time("2024-06-01 13:00:00"):  # Saturday, 3 hours later
        done = invoices.create_invoice(GenerateInvoiceRequestDto(ok.ticket.id, w.exit.id))
        wrong_gate = invoices.create_invoice(GenerateInvoiceRequestDto(ok.ticket.id, w.entry.id))
    assert done.status is ResponseStatus.SUCCESS and done.invoice.amount == 70 + 200
    assert wrong_gate.status is ResponseStatus.FAILURE and wrong_gate.invoice is None

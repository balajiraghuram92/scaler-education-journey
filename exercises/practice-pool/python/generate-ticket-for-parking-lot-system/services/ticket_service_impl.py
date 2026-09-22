from datetime import datetime

from exceptions import NotFoundError, InvalidGateException
from models import VehicleType, Ticket, Gate, GateType, Vehicle
from repositories import TicketRepository, GateRepository, VehicleRepository, ParkingLotRepository
from strategies import SpotAssignmentStrategy
from .ticket_service import TicketService


class TicketServiceImpl(TicketService):
    gate_repository: GateRepository
    vehicle_repository: VehicleRepository
    parking_lot_repository: ParkingLotRepository
    ticket_repository: TicketRepository
    spot_assignment_strategy: SpotAssignmentStrategy

    def __init__(
            self,
            gate_repository: GateRepository,
            vehicle_repository: VehicleRepository,
            parking_lot_repository: ParkingLotRepository,
            ticket_repository: TicketRepository,
            spot_assignment_strategy: SpotAssignmentStrategy
    ):
        self.gate_repository = gate_repository
        self.vehicle_repository = vehicle_repository
        self.parking_lot_repository = parking_lot_repository
        self.ticket_repository = ticket_repository
        self.spot_assignment_strategy = spot_assignment_strategy

    def generate_ticket(
            self,
            gate_id: int,
            number_plate: str,
            vehicle_type: VehicleType
    ) -> Ticket:
        gate: Gate = self.gate_repository.find_by_id(gate_id)
        if gate is None:
            raise NotFoundError("Invalid gate id")

        if gate.gate_type == GateType.EXIT:
            raise InvalidGateException("Exit gate cannot generate ticket")

        vehicle = self.vehicle_repository.find_one(
            number_plate=number_plate,
            vehicle_type=vehicle_type
        )

        if vehicle is None:
            vehicle = Vehicle(
                number_plate=number_plate,
                vehicle_type=vehicle_type
            )
            vehicle = self.vehicle_repository.create(vehicle)

        parking_lot = gate.parking_lot

        parking_spot = self.spot_assignment_strategy.assign_spot(
            parking_lot=parking_lot,
            vehicle_type=vehicle_type
        )

        if parking_spot is None:
            raise NotFoundError("No parking spot available")

        ticket = Ticket(
            vehicle=vehicle,
            coordinator=gate.coordinator,
            entry_time=datetime.now(),
            gate=gate,
            parking_spot=parking_spot
        )

        ticket = self.ticket_repository.create(ticket)

        return ticket

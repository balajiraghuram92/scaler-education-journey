from datetime import datetime
from typing import Union
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from exceptions.parking_spot_not_available_exception import ParkingSpotNotAvailableException
from models.gate_type import GateType
from models.ticket import Ticket
from models.vehicle import Vehicle
from models.vehicle_type import VehicleType
from repositories.gate_repository import GateRepository
from repositories.parking_lot_repository import ParkingLotRepository
from repositories.ticket_repository import TicketRepository
from repositories.vehicle_repository import VehicleRepository
from services.ticket_service import TicketService
from strategies.spot_assignment_strategy import SpotAssignmentStrategy


class TicketServiceImpl(TicketService):
    """
    Implementation of the TicketService domain logic.
    """

    def __init__(
        self,
        gate_repository: GateRepository,
        parking_lot_repository: ParkingLotRepository,
        vehicle_repository: VehicleRepository,
        ticket_repository: TicketRepository,
        spot_assignment_strategy: SpotAssignmentStrategy
    ):
        self.gate_repository = gate_repository
        self.parking_lot_repository = parking_lot_repository
        self.vehicle_repository = vehicle_repository
        self.ticket_repository = ticket_repository
        self.spot_assignment_strategy = spot_assignment_strategy

    def generate_ticket(self, gate_id: int, registration_number: str, vehicle_type: Union[str, VehicleType]) -> Ticket:
        """
        Generates a ticket for an incoming vehicle at an entry gate:
          1. Validates that the gate exists and is an ENTRY gate.
          2. Validates that the gate belongs to a valid parking lot.
          3. Parses and validates the vehicle type.
          4. Finds or creates the vehicle record.
          5. Assigns an available parking spot via the spot assignment strategy.
          6. Creates, stores, and returns the ticket.
        """
        # Step 1: Validate Gate
        gate = self.gate_repository.find_by_id(gate_id)
        if gate is None:
            raise InvalidGateException(f"Gate with id {gate_id} does not exist.")
        if gate.gate_type != GateType.ENTRY:
            raise InvalidGateException(f"Gate with id {gate_id} is not an entry gate.")

        # Step 2: Validate Parking Lot
        parking_lot = self.parking_lot_repository.get_parking_lot_by_gate_id(gate_id)
        if parking_lot is None:
            raise InvalidParkingLotException(f"No parking lot found for gate id {gate_id}.")

        # Step 3: Parse Vehicle Type
        if isinstance(vehicle_type, VehicleType):
            vt_enum = vehicle_type
        else:
            try:
                vt_enum = VehicleType[vehicle_type.upper()]
            except (KeyError, AttributeError):
                raise ValueError(f"Invalid vehicle type: {vehicle_type}")

        # Step 4: Find or Create Vehicle
        vehicle = self.vehicle_repository.get_vehicle_by_registration_number(registration_number)
        if vehicle is None:
            vehicle = self.vehicle_repository.save(
                Vehicle(registration_number=registration_number, vehicle_type=vt_enum)
            )

        # Step 5: Assign Spot
        spot = self.spot_assignment_strategy.assign_spot(parking_lot, vt_enum)
        if spot is None:
            raise ParkingSpotNotAvailableException(f"No available spot for {vt_enum.value} in the parking lot.")

        # Step 6: Create and Save Ticket
        ticket = Ticket(
            vehicle=vehicle,
            entry_time=datetime.now(),
            parking_spot=spot,
            gate=gate,
            parking_attendant=gate.parking_attendant
        )
        return self.ticket_repository.save(ticket)

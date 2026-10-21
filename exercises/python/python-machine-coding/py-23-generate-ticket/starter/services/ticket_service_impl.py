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

    def __init__(self, gate_repository: GateRepository, parking_lot_repository: ParkingLotRepository, vehicle_repository: VehicleRepository, ticket_repository: TicketRepository, spot_assignment_strategy: SpotAssignmentStrategy):
        """Keep the gate, parking lot, vehicle and ticket repositories and the spot assignment strategy."""
        raise NotImplementedError('TODO: implement __init__')

    def generate_ticket(self, gate_id: int, registration_number: str, vehicle_type: Union[str, VehicleType]) -> Ticket:
        """Validate the gate (missing or not ENTRY: InvalidGateException) and its parking lot (InvalidParkingLotException). Parse vehicle_type (string or enum, bad value: ValueError). Find or create the Vehicle. Assign a spot with the strategy (None: ParkingSpotNotAvailableException) and save a Ticket with the entry time, spot, gate and the gate's attendant."""
        raise NotImplementedError('TODO: implement generate_ticket')

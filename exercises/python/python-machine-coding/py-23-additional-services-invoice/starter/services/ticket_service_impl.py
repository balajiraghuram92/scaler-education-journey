from datetime import datetime
from typing import List, Optional, Union
from exceptions.additional_service_not_supported_by_vehicle import AdditionalServiceNotSupportedByVehicle
from exceptions.invalid_gate_exception import InvalidGateException
from exceptions.invalid_parking_lot_exception import InvalidParkingLotException
from exceptions.parking_spot_not_available_exception import ParkingSpotNotAvailableException
from exceptions.unsupported_additional_service import UnsupportedAdditionalService
from models.additional_service import AdditionalService
from models.gate_type import GateType
from models.parking_spot_status import ParkingSpotStatus
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
    Concrete implementation of TicketService supporting additional services.
    """

    def __init__(self, gate_repository: GateRepository, vehicle_repository: VehicleRepository, spot_assignment_strategy: SpotAssignmentStrategy, parking_lot_repository: ParkingLotRepository, ticket_repository: TicketRepository):
        """Keep the gate, vehicle, parking lot and ticket repositories and the spot assignment strategy."""
        raise NotImplementedError('TODO: implement __init__')

    def generate_ticket(self, gate_id: int, registration_number: str, vehicle_type: Union[str, VehicleType], additional_services: Optional[List[Union[str, AdditionalService]]]=None) -> Ticket:
        """Validate the gate (missing or EXIT: InvalidGateException). Parse the vehicle type (invalid: ValueError) and every requested service (unknown: UnsupportedAdditionalService; not in service.supported_vehicle_types: AdditionalServiceNotSupportedByVehicle) before touching any spot. Find or create the vehicle, find the lot (InvalidParkingLotException), assign a spot (None: ParkingSpotNotAvailableException), mark it OCCUPIED and save a Ticket that records the parsed services."""
        raise NotImplementedError('TODO: implement generate_ticket')

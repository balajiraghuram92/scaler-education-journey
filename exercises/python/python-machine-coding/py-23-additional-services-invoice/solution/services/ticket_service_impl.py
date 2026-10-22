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

    def __init__(
        self,
        gate_repository: GateRepository,
        vehicle_repository: VehicleRepository,
        spot_assignment_strategy: SpotAssignmentStrategy,
        parking_lot_repository: ParkingLotRepository,
        ticket_repository: TicketRepository
    ):
        self.gate_repository = gate_repository
        self.vehicle_repository = vehicle_repository
        self.spot_assignment_strategy = spot_assignment_strategy
        self.parking_lot_repository = parking_lot_repository
        self.ticket_repository = ticket_repository

    def generate_ticket(
        self,
        gate_id: int,
        registration_number: str,
        vehicle_type: Union[str, VehicleType],
        additional_services: Optional[List[Union[str, AdditionalService]]] = None
    ) -> Ticket:
        """
        Generates a ticket with validation for gate, vehicle, parking lot, and additional services.
        """
        # Step 1: Validate Gate
        gate = self.gate_repository.find_by_id(gate_id)
        if gate is None:
            raise InvalidGateException(f"Gate with id {gate_id} not found.")
        if gate.gate_type == GateType.EXIT:
            raise InvalidGateException("Vehicle trying to enter from exit gate")

        # Step 2: Parse VehicleType
        if isinstance(vehicle_type, VehicleType):
            vt_enum = vehicle_type
        else:
            clean_vt = str(vehicle_type).upper().strip().replace(" ", "_")
            try:
                vt_enum = VehicleType[clean_vt]
            except (KeyError, AttributeError):
                try:
                    vt_enum = VehicleType(clean_vt)
                except ValueError:
                    raise ValueError(f"Invalid vehicle type: {vehicle_type}")

        # Step 3: Validate and Parse Additional Services
        parsed_services: List[AdditionalService] = []
        if additional_services:
            for service in additional_services:
                if isinstance(service, AdditionalService):
                    svc = service
                else:
                    clean_svc = str(service).upper().strip().replace(" ", "_")
                    try:
                        svc = AdditionalService[clean_svc]
                    except (KeyError, AttributeError):
                        try:
                            svc = AdditionalService(clean_svc)
                        except ValueError:
                            raise UnsupportedAdditionalService(f"Unsupported additional service: {service}")

                if vt_enum not in svc.supported_vehicle_types:
                    raise AdditionalServiceNotSupportedByVehicle(
                        f"Service {svc.value} is not supported for vehicle type {vt_enum.value}"
                    )
                parsed_services.append(svc)

        # Step 4: Find or Create Vehicle
        vehicle = self.vehicle_repository.get_vehicle_by_registration_number(registration_number)
        if vehicle is None:
            vehicle = self.vehicle_repository.save(
                Vehicle(registration_number=registration_number, vehicle_type=vt_enum)
            )

        # Step 5: Validate Parking Lot
        parking_lot = self.parking_lot_repository.get_parking_lot_by_gate_id(gate_id)
        if parking_lot is None:
            raise InvalidParkingLotException(f"No parking lot found for gate id {gate_id}.")

        # Step 6: Assign Spot
        spot = self.spot_assignment_strategy.assign_spot(parking_lot, vt_enum)
        if spot is None:
            raise ParkingSpotNotAvailableException("No parking spot available")
        spot.status = ParkingSpotStatus.OCCUPIED

        # Step 7: Create and Save Ticket
        ticket = Ticket(
            vehicle=vehicle,
            entry_time=datetime.now(),
            parking_spot=spot,
            gate=gate,
            parking_attendant=gate.parking_attendant,
            additional_services=parsed_services
        )
        return self.ticket_repository.save(ticket)

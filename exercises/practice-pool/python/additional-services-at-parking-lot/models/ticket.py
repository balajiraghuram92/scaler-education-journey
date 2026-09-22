from datetime import datetime
from typing import List

from .additional_service import AdditionalService
from .base_model import BaseModel
from .coordinator import Coordinator
from .gate import Gate
from .parking_spot import ParkingSpot
from .vehicle import Vehicle


class Ticket(BaseModel):
    vehicle: Vehicle
    coordinator: Coordinator
    entry_time: datetime
    parking_spot: ParkingSpot
    gate: Gate
    additional_services: List[AdditionalService]

    def __init__(
            self,
            vehicle: Vehicle,
            coordinator: Coordinator,
            entry_time: datetime,
            parking_spot: ParkingSpot,
            gate: Gate,
            additional_services: List[AdditionalService] = None,
            id: int = None
    ):
        super().__init__(id)
        self.vehicle = vehicle
        self.coordinator = coordinator
        self.entry_time = entry_time
        self.parking_spot = parking_spot
        self.gate = gate
        if additional_services is None:
            self.additional_services = []
        else:
            self.additional_services = additional_services

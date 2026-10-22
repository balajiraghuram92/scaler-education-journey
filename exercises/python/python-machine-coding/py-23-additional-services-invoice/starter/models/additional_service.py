from enum import Enum
from typing import List
from models.vehicle_type import VehicleType


class AdditionalService(Enum):
    """
    Represents optional value-added services available at the parking lot.
    Each service has a fixed cost and a set of supported vehicle types.
    """
    CAR_WASH = "CAR_WASH"
    BIKE_WASH = "BIKE_WASH"
    CAR_DETAILING = "CAR_DETAILING"
    EV_BIKE_CHARGING = "EV_BIKE_CHARGING"
    EV_CAR_CHARGING = "EV_CAR_CHARGING"

    @property
    def cost(self) -> float:
        costs = {
            AdditionalService.CAR_WASH: 200.0,
            AdditionalService.BIKE_WASH: 100.0,
            AdditionalService.CAR_DETAILING: 500.0,
            AdditionalService.EV_BIKE_CHARGING: 100.0,
            AdditionalService.EV_CAR_CHARGING: 200.0,
        }
        return costs[self]

    @property
    def supported_vehicle_types(self) -> List[VehicleType]:
        supported = {
            AdditionalService.CAR_WASH: [VehicleType.CAR, VehicleType.SUV],
            AdditionalService.BIKE_WASH: [VehicleType.EV_BIKE, VehicleType.BIKE],
            AdditionalService.CAR_DETAILING: [VehicleType.CAR, VehicleType.SUV],
            AdditionalService.EV_BIKE_CHARGING: [VehicleType.EV_BIKE],
            AdditionalService.EV_CAR_CHARGING: [VehicleType.EV_CAR],
        }
        return supported[self]

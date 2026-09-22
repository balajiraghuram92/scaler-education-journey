from enum import Enum

from .vehicle_type import VehicleType


class AdditionalService(Enum):
    CAR_WASH = ([VehicleType.Car, VehicleType.SUV], 200)
    BIKE_WASH = ([VehicleType.Bike, VehicleType.EV_Bike], 100)
    CAR_DETAILING =([VehicleType.Car, VehicleType.SUV], 500)
    EV_BIKE_CHARGE = ([VehicleType.EV_Bike], 100)
    EV_CAR_CHARGE = ([VehicleType.EV_Car], 200)
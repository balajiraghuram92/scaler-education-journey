from typing import List, Dict, Tuple

from models import VehicleType, ParkingFloor
from repositories import ParkingLotRepository, ParkingSpotRepository
from repositories import ParkingFloorRepository
from .parking_lot_service import ParkingLotService

from exceptions import NotFoundError


class ParkingLotServiceImpl(ParkingLotService):
    parking_lot_repository: ParkingLotRepository
    parking_floor_repository: ParkingFloorRepository
    parking_spot_repository: ParkingSpotRepository

    def __init__(
            self,
            parking_lot_repository,
            parking_floor_repository,
            parking_spot_repository
    ):
        self.parking_lot_repository = parking_lot_repository
        self.parking_floor_repository = parking_floor_repository
        self.parking_spot_repository = parking_spot_repository

    def get_parking_lot_capacity(
            self,
            parking_lot_id: int,
            parking_floor_ids: List[int] = None,
            vehicle_types: List[VehicleType] = None,
            ) -> Dict[ParkingFloor, Dict[VehicleType, int]]:

        parking_lot = self.parking_lot_repository.find_by_id(parking_lot_id)
        if parking_lot is None:
            raise NotFoundError('Parking Lot', parking_lot_id)

        if parking_floor_ids is None:
            parking_floors = self.parking_floor_repository.find(parking_lot=parking_lot)
        else:
            parking_floors = [
                self.parking_floor_repository.find_by_id(parking_floor_id)
                for parking_floor_id in parking_floor_ids
            ]

        capacity = {}

        for parking_floor in parking_floors:
            spots = self.parking_spot_repository.find(
                parking_floor=parking_floor
            )
            vehicle_type_count = {}
            for spot in spots:
                if vehicle_types is None or spot.vehicle_type in vehicle_types:
                    if spot.vehicle_type not in vehicle_type_count:
                        vehicle_type_count[spot.vehicle_type] = 0
                    vehicle_type_count[spot.vehicle_type] += 1
            capacity[parking_floor] = vehicle_type_count

        return capacity

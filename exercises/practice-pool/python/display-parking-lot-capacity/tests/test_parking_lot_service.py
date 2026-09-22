import unittest

from models import VehicleType, ParkingLot, ParkingSpot, ParkingFloor, \
    ParkingSpotStatus
from repositories import ParkingFloorRepository
from repositories import ParkingLotRepository
from repositories import ParkingSpotRepository
from services import ParkingLotServiceImpl


class TestParkingLotService(unittest.TestCase):

    def setUp(self):

        self.parking_lot_repository = ParkingLotRepository()
        self.parking_spot_repository = ParkingSpotRepository()
        self.parking_floor_repository = ParkingFloorRepository()

        self.parking_lot_service = ParkingLotServiceImpl(
            parking_lot_repository=self.parking_lot_repository,
            parking_floor_repository=self.parking_floor_repository,
            parking_spot_repository=self.parking_spot_repository
        )

        self.init_data()

    def test_parking_lot_capacity(self):
        parking_lot = self.data["parking_lot"]

        capacity = self.parking_lot_service.get_parking_lot_capacity(
            parking_lot.id
        )

        self.assertIsInstance(capacity, dict)
        self.assertEqual(len(capacity.keys()), 2)

    def test_parking_lot_capacity_with_floor_ids(self):
        parking_lot = self.data["parking_lot"]
        parking_floors = self.data["parking_floors"]

        capacity = self.parking_lot_service.get_parking_lot_capacity(
            parking_lot.id,
            [parking_floors[0].id]
        )

        self.assertIsInstance(capacity, dict)
        self.assertEqual(len(capacity.keys()), 1)
        self.assertEqual(capacity[parking_floors[0]][VehicleType.Car], 10)
        self.assertEqual(capacity[parking_floors[0]][VehicleType.Bike], 5)

    def test_parking_lot_capacity_with_vehicle_types(self):
        parking_lot = self.data["parking_lot"]
        parking_floors = self.data["parking_floors"]

        capacity = self.parking_lot_service.get_parking_lot_capacity(
            parking_lot.id,
            vehicle_types=[VehicleType.Car, VehicleType.EV_Car]
        )

        self.assertIsInstance(capacity, dict)
        self.assertEqual(len(capacity.keys()), 2)
        self.assertEqual(capacity[parking_floors[0]][VehicleType.Car], 10)
        self.assertEqual(capacity[parking_floors[1]][VehicleType.EV_Car], 11)

    def init_data(self):

        parking_lot1 = self.parking_lot_repository.create(
            ParkingLot(
                name="Parking Lot 1",
                address="Address 1"
            )
        )

        parking_floor1 = ParkingFloor(
            floor_name="Floor 1",
            parking_lot=parking_lot1
        )

        # 10 car spots om floor 1
        for i in range(10):
            self.parking_spot_repository.create(
                ParkingSpot(
                    spot_name=f"A{i}",
                    parking_lot=parking_lot1,
                    parking_floor=parking_floor1,
                    parking_spot_status=ParkingSpotStatus.FREE,
                    vehicle_type=VehicleType.Car
                )
            )
        # 5 bike spots on floor 1
        for i in range(5):
            self.parking_spot_repository.create(
                ParkingSpot(
                    spot_name=f"B{i}",
                    parking_lot=parking_lot1,
                    parking_floor=parking_floor1,
                    parking_spot_status=ParkingSpotStatus.FREE,
                    vehicle_type=VehicleType.Bike
                )
            )

        parking_floor2 = ParkingFloor(
            floor_name="Floor 2",
            parking_lot=parking_lot1
        )

        # 20 bike spots on floor 2
        for i in range(20):
            self.parking_spot_repository.create(
                ParkingSpot(
                    spot_name=f"B{i}",
                    parking_lot=parking_lot1,
                    parking_floor=parking_floor2,
                    parking_spot_status=ParkingSpotStatus.FREE,
                    vehicle_type=VehicleType.Bike
                )
            )

        # 11 EV Car spots on floor 2
        for i in range(11):
            self.parking_spot_repository.create(
                ParkingSpot(
                    spot_name=f"EV{i}",
                    parking_lot=parking_lot1,
                    parking_floor=parking_floor2,
                    parking_spot_status=ParkingSpotStatus.FREE,
                    vehicle_type=VehicleType.EV_Car
                )
            )

        self.parking_floor_repository.create(parking_floor1)
        self.parking_floor_repository.create(parking_floor2)

        self.data = {
            "parking_lot": parking_lot1,
            "parking_floors": [parking_floor1, parking_floor2]
        }

import unittest

from models import Vehicle, VehicleType, Gate, ParkingLot, Coordinator
from models import GateType, ParkingSpot, ParkingFloor, ParkingSpotStatus
from repositories import GateRepository, VehicleRepository, ParkingLotRepository
from repositories import TicketRepository, ParkingSpotRepository
from services import TicketServiceImpl
from strategies import RandomSpotAssignmentStrategy
from exceptions import NotFoundError, UnsupportedAdditionalService


class TestTicketService(unittest.TestCase):

    def setUp(self):
        self.gate_repository = GateRepository()
        self.vehicle_repository = VehicleRepository()
        self.parking_lot_repository = ParkingLotRepository()
        self.ticket_repository = TicketRepository()
        self.parking_spot_repository =ParkingSpotRepository()
        self.spot_assignment_strategy = RandomSpotAssignmentStrategy(
            parking_spot_repository=self.parking_spot_repository
        )

        self.ticket_service = TicketServiceImpl(
            gate_repository=self.gate_repository,
            vehicle_repository=self.vehicle_repository,
            parking_lot_repository=self.parking_lot_repository,
            ticket_repository=self.ticket_repository,
            spot_assignment_strategy=self.spot_assignment_strategy
        )

        self.init_data()

    def test_generate_ticket(self):
        car = self.data["car"]
        entry_gate = self.data["entry_gate"]
        ticket = self.ticket_service.generate_ticket(
                gate_id=entry_gate.id,
                number_plate=car.number_plate,
                vehicle_type=car.vehicle_type
        )

        self.assertEqual(ticket.vehicle, car)

    def test_generate_ticket_spot_not_available(self):
        bike = self.data["bike"]
        entry_gate = self.data["entry_gate"]

        with self.assertRaises(NotFoundError):
            ticket = self.ticket_service.generate_ticket(
                    gate_id=entry_gate.id,
                    number_plate=bike.number_plate,
                    vehicle_type=bike.vehicle_type
            )


    def init_data(self):

        car = self.vehicle_repository.create(
            Vehicle(
                number_plate="KA01HH1234",
                vehicle_type=VehicleType.Car
            )
        )

        bike = self.vehicle_repository.create(
            Vehicle(
                number_plate="KA01HH1235",
                vehicle_type=VehicleType.Bike
            )
        )

        truck = self.vehicle_repository.create(
            Vehicle(
                number_plate="KA01HH1236",
                vehicle_type=VehicleType.SUV
            )
        )

        coordinator = Coordinator(
            name="Coordinator 1",
            email="test@gmail.com"
        )

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

        parking_spot1 = self.parking_spot_repository.create(
            ParkingSpot(
                spot_name="A1",
                parking_lot=parking_lot1,
                parking_floor=parking_floor1,
                parking_spot_status=ParkingSpotStatus.FREE,
                vehicle_type=VehicleType.Car
            )
        )

        entry_gate = self.gate_repository.create(
            Gate(
                name="Entry Gate",
                parking_lot=parking_lot1,
                coordinator=coordinator,
                gate_type=GateType.ENTRY
            )
        )

        exit_gate = self.gate_repository.create(
            Gate(
                name="Exit Gate",
                parking_lot=parking_lot1,
                coordinator=coordinator,
                gate_type=GateType.EXIT
            )
        )

        self.data = {
            "car": car,
            "bike": bike,
            "truck": truck,
            "coordinator": coordinator,
            "parking_lot1": parking_lot1,
            "entry_gate": entry_gate,
            "exit_gate": exit_gate
        }







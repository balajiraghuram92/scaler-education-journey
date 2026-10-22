from dtos.make_booking_request_dto import MakeBookingRequestDto
from dtos.make_booking_response_dto import MakeBookingResponseDto
from dtos.response_status import ResponseStatus
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.invalid_room_exception import InvalidRoomException
from services.booking_service import BookingService

class BookingController:
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    def make_booking(self, request_dto: MakeBookingRequestDto) -> MakeBookingResponseDto:
        response = MakeBookingResponseDto()
        try:
            booking = self.booking_service.make_booking(
                request_dto.user_id, 
                request_dto.booked_rooms
            )
            response.booking = booking
            response.response_status = ResponseStatus.SUCCESS
        except (UserNotFoundException, InvalidRoomException):
            response.booking = None
            response.response_status = ResponseStatus.FAILURE
            
        return response

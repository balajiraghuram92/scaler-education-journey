from dtos.make_booking_request_dto import MakeBookingRequestDto
from dtos.make_booking_response_dto import MakeBookingResponseDto
from dtos.response_status import ResponseStatus
from exceptions.user_not_found_exception import UserNotFoundException
from exceptions.invalid_room_exception import InvalidRoomException
from services.booking_service import BookingService

class BookingController:

    def __init__(self, booking_service: BookingService):
        raise NotImplementedError('TODO: implement __init__')

    def make_booking(self, request_dto: MakeBookingRequestDto) -> MakeBookingResponseDto:
        """SUCCESS with the booking, or FAILURE with booking=None when the service raises UserNotFoundException or InvalidRoomException."""
        raise NotImplementedError('TODO: implement make_booking')

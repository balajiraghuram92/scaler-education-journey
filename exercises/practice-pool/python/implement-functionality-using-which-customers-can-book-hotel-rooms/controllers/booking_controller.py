from services import BookingService
from dtos import MakeBookingRequestDto
from dtos import MakeBookingResponseDto
from dtos import ResponseStatus


class BookingController:
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    def make_booking(self, request_dto: MakeBookingRequestDto) -> MakeBookingResponseDto:

        response_dto: MakeBookingResponseDto = MakeBookingResponseDto()

        try:
            booking = self.booking_service.make_booking(
                user_id=request_dto.user_id,
                rooms_to_be_booked=request_dto.rooms_to_be_booked
            )

            response_dto.response_status = ResponseStatus.SUCCESS
            response_dto.booking = booking

        except Exception as e:
            print(e)
            response_dto.response_status = ResponseStatus.FAILURE

        return response_dto

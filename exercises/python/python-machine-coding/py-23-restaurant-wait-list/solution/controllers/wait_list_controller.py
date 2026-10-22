from dtos.add_user_to_wait_list_request_dto import AddUserToWaitListRequestDto
from dtos.add_user_to_wait_list_response_dto import AddUserToWaitListResponseDto
from dtos.get_user_wait_list_request_dto import GetUserWaitListRequestDto
from dtos.get_user_wait_list_response_dto import GetUserWaitListResponseDto
from dtos.update_wait_list_request_dto import UpdateWaitListRequestDto
from dtos.update_wait_list_response_dto import UpdateWaitListResponseDto
from dtos.response_status import ResponseStatus
from services.wait_list_service import WaitListService


class WaitListController:
    """
    The entry point for all three wait list operations.
    The controller itself has no business logic — it only:
      1. Passes request data to the service
      2. Catches exceptions from the service
      3. Wraps the result into the appropriate response DTO
    """

    def __init__(self, wait_list_service: WaitListService):
        self.wait_list_service = wait_list_service

    def add_user_to_wait_list(self, request: AddUserToWaitListRequestDto) -> AddUserToWaitListResponseDto:
        """Handles a request to add a customer to the wait list."""
        try:
            # Step 1: Extract user_id from the request
            user_id = request.user_id

            # Step 2: Delegate to the service — raises UserNotFoundException if user not found
            position = self.wait_list_service.add_user_to_wait_list(user_id)

            # Step 3: Success — return position and SUCCESS status
            return AddUserToWaitListResponseDto(
                response_status=ResponseStatus.SUCCESS,
                position=position,
            )

        except Exception:
            # Step 4: Any exception (user not found, etc.) → FAILURE response
            return AddUserToWaitListResponseDto(
                response_status=ResponseStatus.FAILURE,
                position=0,
            )

    def get_wait_list_status(self, request: GetUserWaitListRequestDto) -> GetUserWaitListResponseDto:
        """Handles a request to get a customer's current position in the wait list."""
        try:
            # Step 1: Extract user_id from the request
            user_id = request.user_id

            # Step 2: Delegate to the service — raises UserNotFoundException if user not found
            # Returns -1 if the user is registered but not in the wait list
            position = self.wait_list_service.get_wait_list_position(user_id)

            # Step 3: Success — return position (could be -1) and SUCCESS status
            return GetUserWaitListResponseDto(
                response_status=ResponseStatus.SUCCESS,
                position=position,
            )

        except Exception:
            # Step 4: Any exception (user not found, etc.) → FAILURE response
            return GetUserWaitListResponseDto(
                response_status=ResponseStatus.FAILURE,
                position=0,
            )

    def update_wait_list(self, request: UpdateWaitListRequestDto) -> UpdateWaitListResponseDto:
        """Handles a request to remove customers from the wait list (admin only)."""
        try:
            # Step 1: Extract user_id and number_of_seats from the request
            user_id = request.user_id
            number_of_seats = request.number_of_seats

            # Step 2: Delegate to the service
            # Raises UserNotFoundException if user not found
            # Raises UnauthorizedAccessException if the user is not an ADMIN
            self.wait_list_service.update_wait_list(user_id, number_of_seats)

            # Step 3: Success — return SUCCESS status
            return UpdateWaitListResponseDto(response_status=ResponseStatus.SUCCESS)

        except Exception:
            # Step 4: Any exception → FAILURE response
            return UpdateWaitListResponseDto(response_status=ResponseStatus.FAILURE)

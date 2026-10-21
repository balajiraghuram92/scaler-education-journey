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
        """Keep the service."""
        raise NotImplementedError('TODO: implement __init__')

    def add_user_to_wait_list(self, request: AddUserToWaitListRequestDto) -> AddUserToWaitListResponseDto:
        """SUCCESS with the position, or FAILURE with position 0 when anything goes wrong."""
        raise NotImplementedError('TODO: implement add_user_to_wait_list')

    def get_wait_list_status(self, request: GetUserWaitListRequestDto) -> GetUserWaitListResponseDto:
        """SUCCESS with the position, or FAILURE with position 0 when anything goes wrong."""
        raise NotImplementedError('TODO: implement get_wait_list_status')

    def update_wait_list(self, request: UpdateWaitListRequestDto) -> UpdateWaitListResponseDto:
        """SUCCESS, or FAILURE when anything goes wrong."""
        raise NotImplementedError('TODO: implement update_wait_list')

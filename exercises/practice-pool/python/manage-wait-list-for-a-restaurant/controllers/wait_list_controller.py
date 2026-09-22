from typing import List

from models import User
from services import WaitListService
from dtos import AddUserToWaitListRequestDto, AddUserToWaitListResponseDto
from dtos import ResponseStatus
from dtos import ProcessWaitListRequestDto, ProcessWaitListResponseDto
from dtos import GetUserPositionRequestDto, GetUserPositionResponseDto


class WaitListController:
    wait_list_service: WaitListService

    def __init__(
            self,
            wait_list_service: WaitListService
    ):
        self.wait_list_service = wait_list_service

    def add_user(self, request_dto: AddUserToWaitListRequestDto):
        try:
            position = self.wait_list_service.add_user_to_wait_list(
                request_dto.user_id
            )

            return AddUserToWaitListResponseDto(
                position=position,
                response_status=ResponseStatus.SUCCESS
            )
        except Exception as e:
            return AddUserToWaitListResponseDto(
                position=None,
                response_status=ResponseStatus.FAILURE
            )

    def process_wait_list(self, request_dto: ProcessWaitListRequestDto):
        try:
            users: List[User] = self.wait_list_service.process_wait_list(
                admin_user_id=request_dto.user_id,
                spots_count=request_dto.number_of_seats
            )

            return ProcessWaitListResponseDto(
                users=users,
                response_status=ResponseStatus.SUCCESS
            )
        except Exception as e:
            return ProcessWaitListResponseDto(
                users=None,
                response_status=ResponseStatus.FAILURE
            )

    def get_user_position(self, request_dto: GetUserPositionRequestDto):
        try:
            position: int = self.wait_list_service.get_wait_list_position(
                user_id=request_dto.user_id
            )

            return GetUserPositionResponseDto(
                position=position,
                response_status=ResponseStatus.SUCCESS
            )
        except Exception as e:
            return GetUserPositionResponseDto(
                position=None,
                response_status=ResponseStatus.FAILURE
            )







from typing import List

from splitwise.services import GroupService
from splitwise.dtos import CreateGroupRequestDto, CreateGroupResponseDto
from splitwise.dtos import DeleteGroupRequestDto, DeleteGroupResponseDto
from splitwise.dtos import ResponseStatus


class GroupController:
    group_service: GroupService

    def __init__(
            self,
            group_service: GroupService
    ):
        self.group_service = group_service

    def create_group(self, request: CreateGroupRequestDto) -> CreateGroupResponseDto:

        try:
            group = self.group_service.create_group(
                user_id=request.user_id,
                group_name=request.group_name,
                group_description=request.group_description
            )

            return CreateGroupResponseDto(
                group=group,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return CreateGroupResponseDto(
                response_status=ResponseStatus.FAILURE
            )

    def delete_group(self, request: DeleteGroupRequestDto) -> DeleteGroupResponseDto:

        try:
            self.group_service.delete_group(
                group_id=request.group_id,
                admin_id=request.admin_id
            )

            return DeleteGroupResponseDto(
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return DeleteGroupResponseDto(
                response_status=ResponseStatus.FAILURE
            )

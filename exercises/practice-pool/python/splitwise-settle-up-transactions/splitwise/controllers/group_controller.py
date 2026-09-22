from typing import List

from splitwise.services import GroupService
from splitwise.dtos import AddMemberRequestDto, AddMemberResponseDto
from splitwise.dtos import RemoveMemberRequestDto, RemoveMemberResponseDto
from splitwise.dtos import FetchMembersRequestDto, FetchMembersResponseDto
from splitwise.dtos import ResponseStatus


class GroupController:
    group_service: GroupService

    def __init__(
            self,
            group_service: GroupService
    ):
        self.group_service = group_service

    def add_member(self, request: AddMemberRequestDto) -> AddMemberResponseDto:

        try:
            group_member = self.group_service.add_member(
                group_id=request.group_id,
                user_id=request.user_id,
                admin_id=request.admin_id
            )

            return AddMemberResponseDto(
                group_member=group_member,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return AddMemberResponseDto(
                response_status=ResponseStatus.FAILURE
            )

    def remove_member(self, request: RemoveMemberRequestDto) -> RemoveMemberResponseDto:

        try:
            group_member = self.group_service.remove_member(
                group_id=request.group_id,
                user_id=request.user_id,
                admin_id=request.admin_id
            )

            return RemoveMemberResponseDto(
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return RemoveMemberResponseDto(
                response_status=ResponseStatus.FAILURE
            )

    def fetch_member_users(self, request: FetchMembersRequestDto) -> FetchMembersResponseDto:

        try:
            users = self.group_service.get_members(
                group_id=request.group_id,
                admin_id=request.admin_id
            )

            return FetchMembersResponseDto(
                users=users,
                response_status=ResponseStatus.SUCCESS
            )

        except Exception as e:
            return FetchMembersResponseDto(
                response_status=ResponseStatus.FAILURE
            )

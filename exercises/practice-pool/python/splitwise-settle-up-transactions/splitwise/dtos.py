from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
from splitwise.models import GroupMember, GroupAdmin, User, Group


class ResponseStatus(Enum):
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"


@dataclass
class AddMemberRequestDto:
    group_id: int
    user_id: int
    admin_id: int


@dataclass
class AddMemberResponseDto:
    group_member: Optional[GroupMember] = field(default=None)
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)


@dataclass
class RemoveMemberRequestDto:
    group_id: int
    user_id: int
    admin_id: int


@dataclass
class RemoveMemberResponseDto:
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)


@dataclass
class FetchMembersRequestDto:
    group_id: int
    admin_id: int


@dataclass
class FetchMembersResponseDto:
    users: List[User] = field(default=None)
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)

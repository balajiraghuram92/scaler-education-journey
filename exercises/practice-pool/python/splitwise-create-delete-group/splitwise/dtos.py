from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from splitwise.models import Group


class ResponseStatus(Enum):
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"


@dataclass
class CreateGroupRequestDto:
    user_id: int
    group_name: str
    group_description:str


@dataclass
class CreateGroupResponseDto:
    group: Optional[Group] = field(default=None)
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)


@dataclass
class DeleteGroupRequestDto:
    group_id: int
    admin_id: int


@dataclass
class DeleteGroupResponseDto:
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)

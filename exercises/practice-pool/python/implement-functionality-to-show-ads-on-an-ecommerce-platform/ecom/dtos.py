from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ecom.models import Advertisement


class ResponseStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


@dataclass
class GetAdvertisementForUserRequestDto:
    user_id: int


@dataclass
class GetAdvertisementForUserResponseDto:
    response_status: ResponseStatus
    ad: Optional[Advertisement] = field(default=None)

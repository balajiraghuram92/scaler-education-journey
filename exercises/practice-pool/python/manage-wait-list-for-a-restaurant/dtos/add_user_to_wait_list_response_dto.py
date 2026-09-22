from dataclasses import dataclass
from typing import Optional

from .response_status import ResponseStatus


@dataclass
class AddUserToWaitListResponseDto:
    position: Optional[int]
    response_status: ResponseStatus

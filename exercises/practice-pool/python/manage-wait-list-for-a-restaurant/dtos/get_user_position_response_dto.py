from dataclasses import dataclass
from typing import Optional

from .response_status import ResponseStatus


@dataclass
class GetUserPositionResponseDto:
    position: Optional[int]
    response_status: ResponseStatus

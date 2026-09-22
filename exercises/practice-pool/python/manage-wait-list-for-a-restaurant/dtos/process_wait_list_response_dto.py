from dataclasses import dataclass
from typing import List, Optional

from models import User
from .response_status import ResponseStatus


@dataclass
class ProcessWaitListResponseDto:
    users: Optional[List[User]]
    response_status: ResponseStatus

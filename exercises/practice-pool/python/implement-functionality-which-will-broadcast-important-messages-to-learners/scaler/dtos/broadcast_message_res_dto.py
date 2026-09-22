from dataclasses import dataclass, field
from typing import List, Optional
from .response_status import ResponseStatus
from scaler.models import Communication


@dataclass
class BroadcastMessageResDto:
    communication: Optional[Communication]
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)


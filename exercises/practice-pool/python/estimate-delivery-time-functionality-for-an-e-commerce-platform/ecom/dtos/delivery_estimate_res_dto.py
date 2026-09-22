from dataclasses import dataclass, field
from typing import Optional

from .response_status import ResponseStatus
from datetime import datetime


@dataclass
class DeliveryEstimateResDto:
    expected_delivery: Optional[datetime] = field(default=None)
    response_status: ResponseStatus = field(default=None)

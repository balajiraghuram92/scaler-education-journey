from dataclasses import dataclass, field
from typing import Optional

from .response_status import ResponseStatus
from ecom.models import Order


@dataclass
class CancelOrderResDto:
    order: Optional[Order] = field(default=None)
    response_status: ResponseStatus = field(default=None)

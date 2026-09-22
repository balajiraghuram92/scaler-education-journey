from dataclasses import dataclass, field
from .response_status import ResponseStatus
from ecom.models import Inventory


@dataclass
class DeleteInventoryResponseDto:
    response_status: ResponseStatus = field(default=None)

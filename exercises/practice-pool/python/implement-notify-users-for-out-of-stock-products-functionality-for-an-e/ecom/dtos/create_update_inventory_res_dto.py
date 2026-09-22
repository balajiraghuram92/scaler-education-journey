from dataclasses import dataclass, field

from ecom.models import Inventory
from .response_status import ResponseStatus


@dataclass
class CreateUpdateInventoryResDto:
    inventory: Inventory = field(default=None)
    response_status: ResponseStatus = field(default=None)

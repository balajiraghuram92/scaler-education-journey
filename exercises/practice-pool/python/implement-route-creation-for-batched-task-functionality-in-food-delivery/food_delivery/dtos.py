from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from food_delivery.models import Location


class ResponseStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


@dataclass
class BuildBatchedTaskRouteRequestDto:
    batched_task_id: int


@dataclass
class BuildBatchedTaskRouteResponseDto:
    response_status: ResponseStatus
    route_to_be_taken: Optional[List[Location]] = field(default=None)

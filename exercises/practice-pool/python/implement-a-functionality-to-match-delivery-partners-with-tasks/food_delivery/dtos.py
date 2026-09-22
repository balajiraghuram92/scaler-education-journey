from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from food_delivery.models import PartnerTaskMapping


class ResponseStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


@dataclass
class MatchPartnerTaskRequestDto:
    partner_ids: List[int]
    task_ids: List[int]


@dataclass
class MatchPartnerTaskResponseDto:
    response_status: ResponseStatus
    partner_task_mappings: Optional[List[PartnerTaskMapping]] = field(default=None)

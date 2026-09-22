from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class GenerateRecommendationsRequestDto:
    product_id: int


@dataclass
class GenerateRecommendationsResponseDto:
    response_status: ResponseStatus
    recommendations: Optional[List[int]] = field(default=None)

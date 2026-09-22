from dataclasses import dataclass, field
from typing import List, Optional
from .response_status import ResponseStatus
from scaler.models import ScheduledLecture


@dataclass
class ScheduleLectureResDto:
    scheduled_lectures: Optional[List[ScheduledLecture]]
    response_status: ResponseStatus = field(default=ResponseStatus.SUCCESS)


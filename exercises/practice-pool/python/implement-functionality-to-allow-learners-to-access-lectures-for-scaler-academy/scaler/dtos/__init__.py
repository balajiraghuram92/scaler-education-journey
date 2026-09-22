from dataclasses import dataclass
from typing import Optional

from scaler.models import LearnerProgress
from .response_status import ResponseStatus


@dataclass
class AccessLectureReqDto:
    learner_id: int
    scheduled_lecture_id: Optional[int]
    lecture_link: Optional[str]


@dataclass
class AccessLectureResDto:
    learner_progress: Optional[LearnerProgress]
    response_status: ResponseStatus

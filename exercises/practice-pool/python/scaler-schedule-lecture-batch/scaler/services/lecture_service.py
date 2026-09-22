from abc import ABC, abstractmethod
from typing import List

from scaler.models import ScheduledLecture


class LectureService(ABC):

    @abstractmethod
    def schedule_lectures(
            self,
            batch_id: int,
            instructor_id: int,
            lecture_ids: List[int]
    ) -> List[ScheduledLecture]:
        pass

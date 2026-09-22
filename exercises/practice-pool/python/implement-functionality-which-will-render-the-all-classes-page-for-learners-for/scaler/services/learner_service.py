from abc import ABC, abstractmethod
from typing import List

from scaler.models.scheduled_lecture import ScheduledLecture


class LearnerService(ABC):

    @abstractmethod
    def fetch_timeline(
            self,
            learner_id: int
    ) -> List[ScheduledLecture]:
        pass

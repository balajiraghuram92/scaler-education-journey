from abc import ABC, abstractmethod

from scaler.models import LearnerProgress


class LectureService(ABC):

    @abstractmethod
    def access_lecture(
            self,
            learner_id: int,
            scheduled_lecture_id: int,
            lecture_link: str
    ) -> LearnerProgress:
        pass

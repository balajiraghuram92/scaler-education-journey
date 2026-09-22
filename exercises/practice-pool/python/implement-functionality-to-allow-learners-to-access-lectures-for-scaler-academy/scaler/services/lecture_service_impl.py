from typing import Optional

from .lecture_service import LectureService
from scaler.exceptions import NotFoundError, UnauthorizedAccessError

from scaler.models import ScheduledLecture, Learner, BatchLearner, LearnerProgress


class LectureServiceImpl(LectureService):
    def access_lecture(self, learner_id: int, scheduled_lecture_id: Optional[int], lecture_link: Optional[str]) -> LearnerProgress:

        learner = Learner.objects.filter(id=learner_id).first()
        if not learner:
            raise NotFoundError("Learner not found")

        if scheduled_lecture_id:
            scheduled_lecture = ScheduledLecture.objects.get(id=scheduled_lecture_id)
        else:
            scheduled_lecture = ScheduledLecture.objects.filter(
                lecture_link=lecture_link
            ).first()

        if not scheduled_lecture:
            raise NotFoundError("Scheduled lecture not found")

        existing_learner_progress = LearnerProgress.objects.filter(
            learner=learner,
            scheduled_lecture=scheduled_lecture
        ).first()

        if existing_learner_progress:
            return existing_learner_progress

        batch_learner: BatchLearner = BatchLearner.objects.filter(learner=learner, batch=scheduled_lecture.batch).first()
        if not batch_learner:
            raise NotFoundError("Learner not part of batch")

        if batch_learner.entry_date > scheduled_lecture.start_time:
            raise UnauthorizedAccessError("Learner cannot access lecture before batch entry date")

        if batch_learner.exit_date and scheduled_lecture.start_time > batch_learner.exit_date:
            raise UnauthorizedAccessError("Lecture has ended")

        learner_progress = LearnerProgress.objects.create(
            scheduled_lecture=scheduled_lecture,
            learner=learner,
            completed_time_seconds=0,
        )

        return learner_progress
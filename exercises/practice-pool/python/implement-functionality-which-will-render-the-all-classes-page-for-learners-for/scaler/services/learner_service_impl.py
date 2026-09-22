from .learner_service import LearnerService
from typing import List

from scaler.models import ScheduledLecture, Learner, BatchLearner


class LearnerServiceImpl(LearnerService):

    def fetch_timeline(
            self,
            learner_id: int
    ) -> List[ScheduledLecture]:

        learner = Learner.objects.filter(id=learner_id).first()

        batch_learner_items = BatchLearner.objects.filter(
            learner=learner
        ).order_by('entry_date')

        scheduled_lectures = []

        for batch_learner_item in batch_learner_items:
            if batch_learner_item.exit_date is None:
                scheduled_lectures += ScheduledLecture.objects.filter(
                    batch=batch_learner_item.batch,
                    start_time__gte=batch_learner_item.entry_date
                )
            else:
                scheduled_lectures += ScheduledLecture.objects.filter(
                    batch=batch_learner_item.batch,
                    start_time__gte=batch_learner_item.entry_date,
                    end_time__lte=batch_learner_item.exit_date
                )

        return scheduled_lectures

from django.db import models
from .base_model import BaseModel
from .scheduled_lecture import ScheduledLecture
from .learner import Learner


class LearnerProgress(BaseModel):
    scheduled_lecture = models.ForeignKey(
        ScheduledLecture,
        on_delete=models.CASCADE,
        related_name='learner_progress'
    )
    learner = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE,
        related_name='learner_progress'
    )
    completed_time_seconds = models.IntegerField(default=0)

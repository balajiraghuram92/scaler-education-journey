from django.db import models
from .base_model import BaseModel
from .exam import Exam
from .exam_status import ExamStatus
from .learner import Learner


class LearnerExam(BaseModel):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score_obtained = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ExamStatus.choices,
    ),
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

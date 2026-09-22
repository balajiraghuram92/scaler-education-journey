from django.db import models

from .exam import Exam
from .base_model import BaseModel


class Question(BaseModel):
    description = models.CharField(max_length=255)
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    score = models.FloatField()

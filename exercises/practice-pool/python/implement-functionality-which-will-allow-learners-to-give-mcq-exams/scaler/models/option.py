from django.db import models

from .question import Question
from .base_model import BaseModel
from .user_type import UserType


class Option(BaseModel):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    is_correct = models.BooleanField(default=False)

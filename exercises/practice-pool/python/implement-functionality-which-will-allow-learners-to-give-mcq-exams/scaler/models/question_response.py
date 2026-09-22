from django.db import models
from .base_model import BaseModel
from .option import Option
from .exam import Exam
from .question import Question
from .option import Option
from .learner import Learner


class QuestionResponse(BaseModel):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    learner = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE
    )
    response = models.ForeignKey(
        Option,
        on_delete=models.CASCADE
    )

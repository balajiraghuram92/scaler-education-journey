from django.db import models

from .batch import Batch
from .base_model import BaseModel
from .communication import Communication
from .learner import Learner


class CommunicationLearner(BaseModel):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    sent_email = models.BooleanField(default=False)
    sent_sms = models.BooleanField(default=False)

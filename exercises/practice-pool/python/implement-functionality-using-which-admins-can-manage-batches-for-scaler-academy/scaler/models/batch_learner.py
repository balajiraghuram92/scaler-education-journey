from django.db import models
from .base_model import BaseModel
from .batch import Batch
from .learner import Learner


class BatchLearner(BaseModel):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    exit_date = models.DateTimeField(null=True)

from django.db import models
from .base_model import BaseModel
from .batch import Batch
from .lecture import Lecture


class ScheduledLecture(BaseModel):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

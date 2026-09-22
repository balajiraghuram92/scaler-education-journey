from django.db import models
from .base_model import BaseModel
from .batch import Batch
from .instructor import Instructor
from .lecture import Lecture


class ScheduledLecture(BaseModel):
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    link = models.CharField(max_length=255)

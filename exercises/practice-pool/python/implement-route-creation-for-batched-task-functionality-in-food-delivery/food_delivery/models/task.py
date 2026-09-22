from django.db import models
from .base_model import BaseModel
from .location import Location
from .batched_task import BatchedTask


class Task(BaseModel):
    location = models.OneToOneField(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    batch = models.ForeignKey(
        BatchedTask,
        on_delete=models.SET_NULL,
        related_name='tasks',
        null=True,
    )

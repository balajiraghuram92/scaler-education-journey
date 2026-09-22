from django.db import models
from .base_model import BaseModel
from .schedule import Schedule


class Batch(BaseModel):
    name = models.CharField(max_length=255)
    schedule = models.CharField(
        choices=Schedule.choices,
        max_length=25
    )

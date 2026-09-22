from django.db import models
from .base_model import BaseModel
from .location import Location


class Task(BaseModel):
    customer_id = models.IntegerField()
    location = models.OneToOneField(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

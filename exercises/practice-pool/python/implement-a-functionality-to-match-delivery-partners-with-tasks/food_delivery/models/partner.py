from django.db import models
from .base_model import BaseModel
from .location import Location


class Partner(BaseModel):
    name = models.CharField(
        max_length=255
    )
    location = models.OneToOneField(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

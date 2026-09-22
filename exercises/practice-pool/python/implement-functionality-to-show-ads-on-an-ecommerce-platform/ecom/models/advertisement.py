from django.db import models
from .base_model import BaseModel
from .preference import Preference


class Advertisement(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    preference = models.ForeignKey(
        Preference,
        on_delete=models.CASCADE,
        related_name='advertisements'
    )

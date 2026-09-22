from django.db import models
from .base_model import BaseModel
from .preference import Preference


class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    preferences = models.ManyToManyField(
        Preference,
        related_name='users'
    )


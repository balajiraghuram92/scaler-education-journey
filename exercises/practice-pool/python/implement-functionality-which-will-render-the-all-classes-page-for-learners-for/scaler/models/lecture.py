from django.db import models
from .base_model import BaseModel


class Lecture(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

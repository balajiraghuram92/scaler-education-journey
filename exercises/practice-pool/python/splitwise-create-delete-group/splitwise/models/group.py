from django.db import models
from .base_model import BaseModel


class Group(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

from django.db import models
from .base_model import BaseModel


class Location(BaseModel):
    latitude = models.FloatField()
    longitude = models.FloatField()
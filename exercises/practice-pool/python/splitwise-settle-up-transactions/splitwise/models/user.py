from django.db import models
from .base_model import BaseModel


class User(BaseModel):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)


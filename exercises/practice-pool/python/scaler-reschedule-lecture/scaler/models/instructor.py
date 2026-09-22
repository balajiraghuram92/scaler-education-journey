from django.db import models
from .base_model import BaseModel


class Instructor(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()

from django.db import models
from .base_model import BaseModel


class Exam(BaseModel):
    name = models.CharField(max_length=255)

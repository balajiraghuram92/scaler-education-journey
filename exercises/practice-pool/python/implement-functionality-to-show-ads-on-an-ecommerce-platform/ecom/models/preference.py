from django.db import models
from .base_model import BaseModel


class Preference(BaseModel):
    category = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



from django.db import models
from .base_model import BaseModel


class BatchedTask(BaseModel):
    batched_at = models.DateTimeField(auto_now_add=True)
